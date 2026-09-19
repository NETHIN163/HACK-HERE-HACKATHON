from typing import List, Optional
from app.models.traffic import TrafficState, VehicleDemand
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork
from app.simulation.traffic_engine import TrafficEngine


class ScenarioEngine:
    """
    Scenario execution engine for traffic surge, accidents, and road closures.
    """

    @staticmethod
    def apply_traffic_surge(
        network: TrafficNetwork,
        engine: TrafficEngine,
        surge_roads: List[str],
        surge_factor: float = 3.0,
        base_demand_rate: float = 20.0,
        steps: int = 5,
    ) -> TrafficState:
        """
        Executes a Traffic Surge scenario on specified roads:
        1. Increases demand on selected roads by surge_factor.
        2. Recalculates vehicle queues, density, travel time.
        3. Returns the updated TrafficState snapshot.
        """
        # Build base demands for all outbound connections
        demands: List[VehicleDemand] = []

        # Standard baseline demand for network
        for road in network.get_all_roads():
            rate = base_demand_rate
            if road.road_id in surge_roads:
                rate *= surge_factor
            demands.append(VehicleDemand(source=road.source, destination=road.destination, rate=rate))

        # Advance engine simulation by specified steps to reflect surge impact
        latest_state: Optional[TrafficState] = None
        for _ in range(steps):
            latest_state = engine.step(demands=demands, dt=1.0)

        return latest_state
