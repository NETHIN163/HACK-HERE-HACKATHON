from typing import Dict, Optional
from app.models.traffic import TrafficState
from app.models.signal import SignalConfiguration, SignalPhase


class ClassicalOptimizer:
    """
    Deterministic rule-based Classical Traffic Signal Optimizer.
    Evaluates junction queues, density, emergency priority requests, and pedestrian crossings
    to produce optimized SignalConfigurations for each junction.
    """

    def __init__(
        self,
        queue_threshold: int = 10,
        congestion_threshold: float = 0.6,
        base_green: float = 30.0,
        base_red: float = 30.0,
        max_green: float = 90.0,
    ):
        self.queue_threshold = queue_threshold
        self.congestion_threshold = congestion_threshold
        self.base_green = base_green
        self.base_red = base_red
        self.max_green = max_green

    def optimize(
        self,
        traffic_state: TrafficState,
        priority_requests: Optional[Dict[str, str]] = None,
    ) -> Dict[str, SignalConfiguration]:
        """
        Processes current TrafficState and produces deterministic SignalConfigurations per junction.
        
        Rules:
        1. Low traffic (queue <= threshold, density <= congestion_threshold): Keeps base green/red duration.
        2. High Queue (> queue_threshold): Increases green duration proportionally.
        3. High Congestion (> congestion_threshold): Allocates additional green time.
        4. Emergency Priority Request: Applies EMERGENCY_PRIORITY phase with priority_override=True.
        5. Active Pedestrian Crossing: Applies PEDESTRIAN_CLEARANCE phase while active.
        """
        configurations: Dict[str, SignalConfiguration] = {}

        for j_id, junc in traffic_state.junctions.items():
            green = self.base_green
            red = self.base_red
            phase = SignalPhase(junc.signal_phase) if junc.signal_phase in SignalPhase.__members__ else SignalPhase.NS_GREEN
            priority_override = False
            reservation_id = None

            # 1. Check Pedestrian Crossing Lock
            if junc.crossing_active and junc.crossing_remaining_seconds > 0:
                phase = SignalPhase.PEDESTRIAN_CLEARANCE
                green = max(self.base_green, junc.crossing_remaining_seconds)
                configurations[j_id] = SignalConfiguration(
                    junction_id=j_id,
                    signal_phase=phase,
                    green_duration=green,
                    red_duration=red,
                    priority_override=False,
                )
                continue

            # 2. Check Emergency Priority Request or Reservation
            is_priority_requested = priority_requests and j_id in priority_requests
            if junc.emergency_reserved or is_priority_requested:
                phase = SignalPhase.EMERGENCY_PRIORITY
                green = self.max_green
                red = 15.0
                priority_override = True
                if is_priority_requested:
                    reservation_id = priority_requests[j_id]
                configurations[j_id] = SignalConfiguration(
                    junction_id=j_id,
                    signal_phase=phase,
                    green_duration=green,
                    red_duration=red,
                    priority_override=priority_override,
                    reservation_id=reservation_id,
                )
                continue

            # 3. High Queue Adjustment
            if junc.queue_length > self.queue_threshold:
                excess_queue = junc.queue_length - self.queue_threshold
                queue_bonus = min(30.0, (excess_queue // 5) * 10.0 + 10.0)
                green += queue_bonus

            # 4. High Congestion Adjustment
            if junc.vehicle_density > self.congestion_threshold:
                congestion_bonus = 20.0
                green += congestion_bonus

            # Cap green duration at max_green
            green = min(self.max_green, green)

            configurations[j_id] = SignalConfiguration(
                junction_id=j_id,
                signal_phase=phase,
                green_duration=green,
                red_duration=red,
                priority_override=priority_override,
                reservation_id=reservation_id,
            )

        return configurations
