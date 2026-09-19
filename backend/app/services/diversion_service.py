from typing import Dict, List, Optional
from app.models.metrics import DiversionImpact
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork


class DiversionService:
    """
    Service estimating downstream traffic, queue, congestion, and risk level
    when vehicles are diverted from a blocked or closed road to alternative routes.
    """

    def __init__(self, network: TrafficNetwork):
        self.network = network

    def estimate_diversion_impact(
        self,
        blocked_road_id: str,
        candidate_roads: Optional[List[str]] = None,
        diverted_vehicle_count: float = 40.0,
    ) -> DiversionImpact:
        """
        Estimates the diversion impact when blocked_road_id is unavailable:
        1. Identifies viable alternative roads excluding BLOCKED/CLOSED roads.
        2. Distributes diverted traffic across alternatives.
        3. Predicts traffic flow, queues, and congestion on alternative roads.
        4. Identifies affected junctions and calculates deterministic risk level.
        """
        blocked_road = self.network.get_road(blocked_road_id)
        if not blocked_road:
            raise ValueError(f"Invalid road ID: '{blocked_road_id}' does not exist in network.")

        source, dest = blocked_road.source, blocked_road.destination

        # 1. Determine candidate alternative roads
        # Find paths from source to dest in network
        available_paths = self.network.find_all_paths(source, dest, ignore_blocked=True)

        alt_road_ids: List[str] = []
        if candidate_roads:
            # Filter user-provided candidates to exclude BLOCKED or CLOSED roads
            for r_id in candidate_roads:
                road = self.network.get_road(r_id)
                if road and road.status not in [RoadStatus.BLOCKED, RoadStatus.CLOSED]:
                    alt_road_ids.append(r_id)
        else:
            # Extract road IDs from available alternative paths
            for path in available_paths:
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    r_id = f"R_{u}_{v}"
                    if r_id != blocked_road_id and r_id in self.network.roads:
                        road = self.network.roads[r_id]
                        if road.status not in [RoadStatus.BLOCKED, RoadStatus.CLOSED] and r_id not in alt_road_ids:
                            alt_road_ids.append(r_id)

        # 2. Predict impact on alternative roads
        predicted_traffic: Dict[str, float] = {}
        predicted_queue: Dict[str, int] = {}
        predicted_congestion: Dict[str, float] = {}
        affected_junctions_set = set()

        if not alt_road_ids:
            # No alternative roads available -> CRITICAL risk
            return DiversionImpact(
                blocked_road_id=blocked_road_id,
                alternative_roads=[],
                predicted_traffic={},
                predicted_queue={},
                predicted_congestion={},
                affected_junctions=[source, dest],
                risk_level="CRITICAL",
            )

        vehicles_per_alt = diverted_vehicle_count / len(alt_road_ids)

        for r_id in alt_road_ids:
            road = self.network.get_road(r_id)
            if not road:
                continue

            affected_junctions_set.add(road.source)
            affected_junctions_set.add(road.destination)

            current_density = road.traffic_density
            cap = max(1.0, road.capacity)

            # Added density from diverted traffic
            added_density = min(1.0, vehicles_per_alt / cap)
            new_density = round(min(1.0, current_density + added_density), 4)

            # Predicted traffic flow
            pred_flow = round(cap * (1.0 - new_density) + vehicles_per_alt, 2)

            # Predicted queue length
            current_queue = road.queue_length
            added_queue = int(max(0.0, (new_density - 0.6) * 15)) if new_density > 0.6 else 0
            pred_queue = current_queue + added_queue

            predicted_traffic[r_id] = pred_flow
            predicted_queue[r_id] = pred_queue
            predicted_congestion[r_id] = new_density

        # 3. Calculate Deterministic Risk Level
        avg_new_congestion = sum(predicted_congestion.values()) / len(predicted_congestion) if predicted_congestion else 1.0

        if avg_new_congestion < 0.4:
            risk_level = "LOW"
        elif avg_new_congestion < 0.7:
            risk_level = "MEDIUM"
        elif avg_new_congestion < 0.85:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        return DiversionImpact(
            blocked_road_id=blocked_road_id,
            alternative_roads=alt_road_ids,
            predicted_traffic=predicted_traffic,
            predicted_queue=predicted_queue,
            predicted_congestion=predicted_congestion,
            affected_junctions=sorted(list(affected_junctions_set)),
            risk_level=risk_level,
        )
