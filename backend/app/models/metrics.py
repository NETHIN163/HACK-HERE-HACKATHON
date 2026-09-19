from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field


class TrafficMetrics(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    average_waiting_time: float = Field(..., description="Average waiting time per road in seconds", ge=0.0)
    average_queue_length: float = Field(..., description="Average vehicle queue length across network", ge=0.0)
    maximum_queue_length: int = Field(..., description="Maximum single queue length in network", ge=0)
    traffic_throughput: float = Field(..., description="Total network vehicle throughput (veh/min)", ge=0.0)
    emergency_delay: float = Field(..., description="Emergency vehicle delay in seconds", ge=0.0)
    emergency_travel_time: float = Field(..., description="Total emergency route travel time in seconds", ge=0.0)
    fuel_estimate: float = Field(..., description="Estimated fuel consumption in Liters", ge=0.0)
    co2_estimate: float = Field(..., description="Estimated CO2 emissions in kg", ge=0.0)
    pedestrian_delay: float = Field(..., description="Total pedestrian delay in seconds", ge=0.0)


class DiversionImpact(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    blocked_road_id: str = Field(..., description="Blocked or closed road ID being diverted from")
    alternative_roads: List[str] = Field(default_factory=list, description="List of viable alternative road IDs")
    predicted_traffic: Dict[str, float] = Field(default_factory=dict, description="Map of road_id to predicted vehicle flow/count")
    predicted_queue: Dict[str, int] = Field(default_factory=dict, description="Map of road_id to predicted queue length")
    predicted_congestion: Dict[str, float] = Field(default_factory=dict, description="Map of road_id to predicted density ratio")
    affected_junctions: List[str] = Field(default_factory=list, description="List of affected junction IDs")
    risk_level: str = Field(..., description="Deterministic diversion risk level: LOW, MEDIUM, HIGH, CRITICAL")
