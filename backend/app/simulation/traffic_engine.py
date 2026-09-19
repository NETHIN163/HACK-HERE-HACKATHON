from typing import Dict, List, Optional
import numpy as np

from app.models.road import Road, RoadStatus
from app.models.junction import Junction
from app.models.traffic import TrafficState, VehicleDemand
from app.models.incident import Incident, IncidentType
from app.simulation.network import TrafficNetwork


class TrafficEngine:
    """
    Deterministic/Seeded Traffic Simulation Engine (Hackathon Abstraction Level).
    Simulates traffic demand, flow, density, queues, travel time, and waiting time.
    """

    def __init__(self, network: TrafficNetwork, seed: int = 42):
        self.network = network
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.simulation_time: float = 0.0
        # Internal state tracking
        self.vehicles_on_road: Dict[str, float] = {r.road_id: 0.0 for r in network.get_all_roads()}
        self.road_waiting_times: Dict[str, float] = {r.road_id: 0.0 for r in network.get_all_roads()}
        self.road_flows: Dict[str, float] = {r.road_id: 0.0 for r in network.get_all_roads()}

    def reset(self, seed: Optional[int] = None) -> None:
        """Resets the simulation engine state and random generator."""
        if seed is not None:
            self.seed = seed
        self.rng = np.random.default_rng(self.seed)
        self.simulation_time = 0.0
        for road in self.network.get_all_roads():
            self.vehicles_on_road[road.road_id] = 0.0
            self.road_waiting_times[road.road_id] = 0.0
            self.road_flows[road.road_id] = 0.0
            road.traffic_density = 0.0
            road.queue_length = 0
            road.status = RoadStatus.OPEN
            road.travel_time = road.distance / 13.89

        for junction in self.network.get_all_junctions():
            junction.queue_length = 0
            junction.vehicle_density = 0.0

    def step(
        self,
        demands: List[VehicleDemand],
        incidents: Optional[List[Incident]] = None,
        dt: float = 1.0,
    ) -> TrafficState:
        """
        Advances the traffic simulation by dt seconds.
        
        Inputs:
        - demands: List of active VehicleDemand models
        - incidents: List of active Incident models (optional)
        - dt: Time step in seconds (default = 1.0s)
        
        Updates:
        - Vehicle flow
        - Queue length
        - Traffic density
        - Travel time
        - Waiting time
        """
        self.simulation_time += dt

        # 1. Process active incidents & update road status
        active_incident_ids = []
        blocked_roads = set()
        if incidents:
            for inc in incidents:
                if inc.active:
                    active_incident_ids.append(inc.incident_id)
                    blocked_roads.add(inc.road_id)
                    road = self.network.get_road(inc.road_id)
                    if road:
                        if inc.type == IncidentType.ACCIDENT:
                            self.network.update_road_status(inc.road_id, RoadStatus.BLOCKED)
                        elif inc.type == IncidentType.ROAD_CLOSURE:
                            self.network.update_road_status(inc.road_id, RoadStatus.CLOSED)

        # 2. Map demand to matching roads
        # Match source/destination demand to outbound roads from source junction
        demand_by_road: Dict[str, float] = {r.road_id: 0.0 for r in self.network.get_all_roads()}
        for d in demands:
            # Find path for demand
            path = self.network.get_shortest_path(d.source, d.destination, ignore_blocked=True)
            if path and len(path) > 1:
                # Assign demand to first road in shortest path
                u, v = path[0], path[1]
                road_id = f"R_{u}_{v}"
                if road_id in demand_by_road:
                    demand_by_road[road_id] += d.rate

        # 3. Simulate flow, density, queues, and travel time per road
        for road in self.network.get_all_roads():
            r_id = road.road_id

            # If road is BLOCKED or CLOSED, flow = 0 and travel time is infinite
            if road.status in [RoadStatus.BLOCKED, RoadStatus.CLOSED]:
                self.road_flows[r_id] = 0.0
                road.traffic_density = 1.0
                # Queued vehicles stay queued, travel time skyrockets
                road.travel_time = 999999.0
                continue

            # Free flow speed = 50 km/h = 13.89 m/s
            free_flow_time = road.distance / 13.89
            max_road_capacity = road.capacity  # veh / min
            max_vehicles_on_road = max(1.0, (road.distance / 7.0))  # approx 7m per vehicle space

            inflow_rate = demand_by_road.get(r_id, 0.0) / 60.0  # convert veh/min to veh/sec
            # Add small deterministic noise if demand > 0
            if inflow_rate > 0:
                noise = self.rng.normal(1.0, 0.02)
                inflow_rate = max(0.0, inflow_rate * noise)

            # Downstream junction signal check
            dest_junction = self.network.get_junction(road.destination)
            outflow_capacity = (max_road_capacity / 60.0)  # veh/sec

            # Check if signal allows outflow
            is_green = True
            if dest_junction:
                try:
                    u_num = int(road.source[1:])
                    v_num = int(road.destination[1:])
                    is_vertical = (abs(u_num - v_num) >= 3)
                except (ValueError, IndexError):
                    is_vertical = False

                if is_vertical and dest_junction.signal_phase == "EW_GREEN":
                    is_green = False
                elif not is_vertical and dest_junction.signal_phase == "NS_GREEN":
                    is_green = False


            if not is_green:
                outflow_rate = 0.0
            else:
                outflow_rate = outflow_capacity

            # Update vehicle count on road
            prev_vehicles = self.vehicles_on_road[r_id]
            net_change = (inflow_rate - outflow_rate) * dt
            new_vehicles = max(0.0, prev_vehicles + net_change)
            self.vehicles_on_road[r_id] = new_vehicles

            # Calculate vehicle flow (actual throughput in veh/min)
            actual_flow = min(inflow_rate, outflow_rate) * 60.0
            self.road_flows[r_id] = actual_flow

            # Calculate queue length
            if not is_green:
                # Accumulate queue when red signal
                road.queue_length = int(min(new_vehicles, max_vehicles_on_road))
                self.road_waiting_times[r_id] += road.queue_length * dt
            else:
                # Discharge queue when green signal
                discharge = int(outflow_capacity * dt * 2)
                road.queue_length = max(0, road.queue_length - discharge)

            # Calculate density
            density = min(1.0, new_vehicles / max_vehicles_on_road)
            road.traffic_density = round(density, 4)

            # Update Road Status based on density
            if road.status not in [RoadStatus.BLOCKED, RoadStatus.CLOSED]:
                if road.traffic_density >= 0.7:
                    road.status = RoadStatus.CONGESTED
                else:
                    road.status = RoadStatus.OPEN

            # Calculate Travel Time using Bureau of Public Roads (BPR) function
            # travel_time = free_flow_time * (1 + 0.15 * (density / 0.8)^4)
            bpr_factor = 1.0 + 0.15 * ((road.traffic_density / 0.8) ** 4)
            road.travel_time = round(free_flow_time * bpr_factor, 2)

        # 4. Update Junction queue lengths and densities
        for j_id, junction in self.network.junctions.items():
            inbound_roads = self.network.get_inbound_roads(j_id)
            if inbound_roads:
                total_queue = sum(r.queue_length for r in inbound_roads)
                avg_density = sum(r.traffic_density for r in inbound_roads) / len(inbound_roads)
                junction.queue_length = total_queue
                junction.vehicle_density = round(avg_density, 4)

        # 5. Build and return TrafficState snapshot
        return TrafficState(
            timestamp=self.simulation_time,
            roads={r_id: road.model_copy() for r_id, road in self.network.roads.items()},
            junctions={j_id: junc.model_copy() for j_id, junc in self.network.junctions.items()},
            active_incidents=active_incident_ids,
        )
