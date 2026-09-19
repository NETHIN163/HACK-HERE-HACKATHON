from typing import Dict, List, Optional
from app.models.road import Road
from app.models.junction import Junction
from app.models.traffic import TrafficState, VehicleDemand
from app.models.signal import SignalConfiguration
from app.models.incident import Incident, IncidentType
from app.models.metrics import TrafficMetrics
from app.simulation.network import TrafficNetwork
from app.simulation.traffic_engine import TrafficEngine
from app.simulation.scenarios import ScenarioEngine
from app.services.incident_service import IncidentService
from app.services.metrics_service import MetricsService
from app.services.diversion_service import DiversionService
from app.optimization.classical import ClassicalOptimizer


class TrafficService:
    """
    Central orchestration service binding Network, TrafficEngine, IncidentService,
    ClassicalOptimizer, MetricsService, and DiversionService together.
    """

    def __init__(self, seed: int = 42):
        self.network = TrafficNetwork()
        self.engine = TrafficEngine(network=self.network, seed=seed)
        self.incident_service = IncidentService(network=self.network)
        self.metrics_service = MetricsService()
        self.diversion_service = DiversionService(network=self.network)
        self.classical_optimizer = ClassicalOptimizer()

    def get_traffic_state(self) -> TrafficState:
        """Runs a simulation step with active demand and returns current TrafficState."""
        active_incidents = self.incident_service.get_all_incidents(active_only=True)
        # Default baseline demand across connected roads
        demands = [
            VehicleDemand(source=r.source, destination=r.destination, rate=15.0)
            for r in self.network.get_all_roads()
            if r.status in ["OPEN", "CONGESTED"]
        ]
        state = self.engine.step(demands=demands, incidents=active_incidents, dt=1.0)
        try:
            from app.websocket.events import broadcast_event
            broadcast_event("traffic.updated", "network", state.model_dump())
        except Exception:
            pass
        return state


    def get_all_junctions(self) -> List[Junction]:
        return self.network.get_all_junctions()

    def get_junction(self, junction_id: str) -> Optional[Junction]:
        return self.network.get_junction(junction_id)

    def get_all_roads(self) -> List[Road]:
        return self.network.get_all_roads()

    def get_road(self, road_id: str) -> Optional[Road]:
        return self.network.get_road(road_id)

    def get_all_incidents(self, active_only: bool = False) -> List[Incident]:
        return self.incident_service.get_all_incidents(active_only=active_only)

    def create_incident(
        self,
        incident_id: str,
        type: str,
        road_id: str,
        severity: float = 1.0,
        description: Optional[str] = None,
    ) -> Incident:
        return self.incident_service.create_incident(
            incident_id=incident_id,
            type=type,
            road_id=road_id,
            severity=severity,
            description=description,
        )

    def update_incident(
        self,
        incident_id: str,
        active: Optional[bool] = None,
        severity: Optional[float] = None,
        description: Optional[str] = None,
    ) -> Incident:
        return self.incident_service.update_incident(
            incident_id=incident_id,
            active=active,
            severity=severity,
            description=description,
        )

    def trigger_traffic_surge(self, surge_roads: List[str], surge_factor: float = 3.0) -> TrafficState:
        # Validate roads exist
        for r_id in surge_roads:
            if not self.network.get_road(r_id):
                raise ValueError(f"Invalid road ID in surge list: '{r_id}'")
        return ScenarioEngine.apply_traffic_surge(
            network=self.network,
            engine=self.engine,
            surge_roads=surge_roads,
            surge_factor=surge_factor,
            base_demand_rate=20.0,
            steps=5,
        )

    def trigger_accident_scenario(self, road_id: str, description: Optional[str] = None) -> Incident:
        inc_id = f"INC_ACC_{int(self.engine.simulation_time) + 1000}"
        return self.create_incident(
            incident_id=inc_id,
            type="ACCIDENT",
            road_id=road_id,
            description=description or "Accident scenario triggered",
        )

    def trigger_road_closure_scenario(self, road_id: str, description: Optional[str] = None) -> Incident:
        inc_id = f"INC_CLS_{int(self.engine.simulation_time) + 2000}"
        return self.create_incident(
            incident_id=inc_id,
            type="ROAD_CLOSURE",
            road_id=road_id,
            description=description or "Road closure scenario triggered",
        )

    def get_metrics(self) -> TrafficMetrics:
        state = self.get_traffic_state()
        return self.metrics_service.calculate_metrics(state, engine=self.engine)

    def get_classical_optimization(self) -> Dict[str, SignalConfiguration]:
        state = self.get_traffic_state()
        return self.classical_optimizer.optimize(state)


# Shared global singleton for API app
traffic_service = TrafficService()
