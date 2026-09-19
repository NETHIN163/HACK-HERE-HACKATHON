from typing import Dict, List
from fastapi import APIRouter
from app.models.traffic import TrafficState
from app.models.junction import Junction
from app.models.road import Road
from app.models.metrics import TrafficMetrics
from app.models.signal import SignalConfiguration
from app.services.traffic_service import traffic_service

router = APIRouter(tags=["traffic"])


@router.get("/api/traffic", response_model=TrafficState)
def get_traffic_state():
    """Returns current overall network traffic state."""
    return traffic_service.get_traffic_state()


@router.get("/api/traffic/junctions", response_model=List[Junction])
def get_all_junctions_traffic():
    """Returns current traffic state for all junctions."""
    return traffic_service.get_all_junctions()


@router.get("/api/traffic/roads", response_model=List[Road])
def get_all_roads_traffic():
    """Returns current traffic state for all roads."""
    return traffic_service.get_all_roads()


@router.get("/api/metrics", response_model=TrafficMetrics)
def get_traffic_metrics():
    """Returns overall traffic and environmental performance metrics."""
    return traffic_service.get_metrics()


@router.get("/api/optimization/classical", response_model=Dict[str, SignalConfiguration])
def get_classical_optimization():
    """Runs ClassicalOptimizer baseline against current traffic state and returns signal configurations."""
    return traffic_service.get_classical_optimization()
