from typing import Dict, List, Optional, Tuple
import networkx as nx

from app.models.junction import Junction
from app.models.road import Road, RoadStatus


class TrafficNetwork:
    """
    NetworkX-based urban traffic network representation.
    Manages 4-8 junctions connected in a multi-path topology.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.junctions: Dict[str, Junction] = {}
        self.roads: Dict[str, Road] = {}
        self._build_default_network()

    def _build_default_network(self) -> None:
        """
        Builds default 6-junction 2x3 grid urban network:
        J1 ─── J2 ─── J3
        │      │       │
        J4 ─── J5 ─── J6
        """
        # Create 6 Junctions J1 to J6
        for i in range(1, 7):
            j_id = f"J{i}"
            junction = Junction(
                junction_id=j_id,
                signal_phase="NS_GREEN" if i % 2 == 1 else "EW_GREEN",
                green_duration=30.0,
                red_duration=30.0,
                queue_length=0,
                vehicle_density=0.1,
                pedestrian_count=0,
                emergency_reserved=False,
            )
            self.junctions[j_id] = junction
            self.graph.add_node(j_id, model=junction)

        # Define 2x3 grid connections (bi-directional edges)
        grid_connections: List[Tuple[str, str, float, float]] = [
            # Horizontal top row
            ("J1", "J2", 500.0, 60.0),  # (source, dest, distance meters, capacity veh/min)
            ("J2", "J3", 500.0, 60.0),
            # Horizontal bottom row
            ("J4", "J5", 500.0, 60.0),
            ("J5", "J6", 500.0, 60.0),
            # Vertical columns
            ("J1", "J4", 400.0, 50.0),
            ("J2", "J5", 400.0, 50.0),
            ("J3", "J6", 400.0, 50.0),
        ]

        for u, v, dist, cap in grid_connections:
            # Forward direction
            road_id_fwd = f"R_{u}_{v}"
            road_fwd = Road(
                road_id=road_id_fwd,
                source=u,
                destination=v,
                distance=dist,
                capacity=cap,
                travel_time=dist / 13.89,  # ~50 km/h = 13.89 m/s -> free flow ~36s for 500m
                traffic_density=0.1,
                queue_length=0,
                status=RoadStatus.OPEN,
            )
            self.roads[road_id_fwd] = road_fwd
            self.graph.add_edge(u, v, road_id=road_id_fwd, weight=road_fwd.travel_time, model=road_fwd)

            # Reverse direction
            road_id_rev = f"R_{v}_{u}"
            road_rev = Road(
                road_id=road_id_rev,
                source=v,
                destination=u,
                distance=dist,
                capacity=cap,
                travel_time=dist / 13.89,
                traffic_density=0.1,
                queue_length=0,
                status=RoadStatus.OPEN,
            )
            self.roads[road_id_rev] = road_rev
            self.graph.add_edge(v, u, road_id=road_id_rev, weight=road_rev.travel_time, model=road_rev)

    def get_junction(self, junction_id: str) -> Optional[Junction]:
        """Retrieves Junction by ID."""
        return self.junctions.get(junction_id)

    def get_road(self, road_id: str) -> Optional[Road]:
        """Retrieves Road by ID."""
        return self.roads.get(road_id)

    def get_all_junctions(self) -> List[Junction]:
        """Returns list of all junctions."""
        return list(self.junctions.values())

    def get_all_roads(self) -> List[Road]:
        """Returns list of all roads."""
        return list(self.roads.values())

    def update_road_status(self, road_id: str, status: RoadStatus) -> Optional[Road]:
        """Updates status of specified road and syncs graph edge attributes."""
        if road_id not in self.roads:
            return None
        road = self.roads[road_id]
        road.status = status
        # Update graph edge model reference
        if self.graph.has_edge(road.source, road.destination):
            self.graph[road.source][road.destination]["model"] = road
            # If blocked or closed, set edge weight high or remove availability
            if status in [RoadStatus.BLOCKED, RoadStatus.CLOSED]:
                self.graph[road.source][road.destination]["weight"] = float("inf")
            else:
                self.graph[road.source][road.destination]["weight"] = road.travel_time
        return road

    def get_outbound_roads(self, junction_id: str) -> List[Road]:
        """Returns all outbound roads originating from specified junction."""
        return [r for r in self.roads.values() if r.source == junction_id]

    def get_inbound_roads(self, junction_id: str) -> List[Road]:
        """Returns all inbound roads terminating at specified junction."""
        return [r for r in self.roads.values() if r.destination == junction_id]

    def find_all_paths(self, source: str, destination: str, ignore_blocked: bool = True) -> List[List[str]]:
        """
        Finds all simple paths from source to destination junction.
        If ignore_blocked is True, filters out paths containing BLOCKED or CLOSED roads.
        Returns a list of junction ID sequences, e.g. [['J1', 'J2', 'J3'], ['J1', 'J4', 'J5', 'J6', 'J3']]
        """
        if source not in self.junctions or destination not in self.junctions:
            return []

        all_paths = list(nx.all_simple_paths(self.graph, source=source, target=destination))
        if not ignore_blocked:
            return all_paths

        valid_paths = []
        for path in all_paths:
            is_valid = True
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = self.graph.get_edge_data(u, v)
                if edge_data and "model" in edge_data:
                    road: Road = edge_data["model"]
                    if road.status in [RoadStatus.BLOCKED, RoadStatus.CLOSED]:
                        is_valid = False
                        break
            if is_valid:
                valid_paths.append(path)

        return valid_paths

    def get_shortest_path(self, source: str, destination: str, ignore_blocked: bool = True) -> Optional[List[str]]:
        """
        Finds the shortest path from source to destination by travel time weight.
        If ignore_blocked is True, avoids BLOCKED or CLOSED roads.
        """
        valid_paths = self.find_all_paths(source=source, destination=destination, ignore_blocked=ignore_blocked)
        if not valid_paths:
            return None

        # Sort paths by total travel time
        def calculate_path_time(path: List[str]) -> float:
            total_time = 0.0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = self.graph.get_edge_data(u, v)
                if edge_data and "model" in edge_data:
                    total_time += edge_data["model"].travel_time
            return total_time

        valid_paths.sort(key=calculate_path_time)
        return valid_paths[0]
