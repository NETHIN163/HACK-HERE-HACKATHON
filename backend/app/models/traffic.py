from typing import Dict, List
from pydantic import BaseModel, Field
from .road import Road
from .junction import Junction


class VehicleDemand(BaseModel):
    source: str = Field(..., description="Source junction ID")
    destination: str = Field(..., description="Destination junction ID")
    rate: float = Field(..., description="Demand flow rate in vehicles per minute", ge=0.0)


class TrafficState(BaseModel):
    timestamp: float = Field(..., description="Simulation timestamp or epoch")
    roads: Dict[str, Road] = Field(default_factory=dict, description="Map of road_id to Road model")
    junctions: Dict[str, Junction] = Field(default_factory=dict, description="Map of junction_id to Junction model")
    active_incidents: List[str] = Field(default_factory=list, description="List of active incident IDs")
