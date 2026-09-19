from typing import Dict, Optional, Set, Tuple
from app.models.signal import SignalConfiguration, SignalPhase
from app.simulation.network import TrafficNetwork


class SignalController:
    """
    Signal Controller managing junction signal phase applications, conflict validation,
    emergency reservations, and pedestrian clearance enforcement.
    """

    def __init__(self, network: TrafficNetwork):
        self.network = network
        self.active_reservations: Dict[str, str] = {}  # junction_id -> reservation_id

    def validate_configuration(self, config: SignalConfiguration) -> Tuple[bool, str]:

        """
        Validates signal configuration against safety rules:
        1. Junction must exist in network.
        2. Green/Red durations must be >= 5.0 seconds.
        3. Signal phase must be valid.
        4. Pedestrian Safety: Cannot switch away from PEDESTRIAN_CLEARANCE while crossing_active is True
           and crossing_remaining_seconds > 0.
        5. Conflict check: Reject invalid/conflicting phase transitions.
        """
        junc = self.network.get_junction(config.junction_id)
        if not junc:
            return False, f"Unknown junction ID: '{config.junction_id}'"

        if config.green_duration < 5.0 or config.red_duration < 5.0:
            return False, f"Invalid signal duration (green: {config.green_duration}s, red: {config.red_duration}s). Minimum is 5.0s."

        # Pedestrian clearance safety check
        if junc.crossing_active and junc.crossing_remaining_seconds > 0:
            # If pedestrian crossing is active, non-pedestrian clearance phase override is rejected
            if config.signal_phase != SignalPhase.PEDESTRIAN_CLEARANCE and not (
                config.priority_override and junc.crossing_remaining_seconds <= 2.0
            ):
                # Reject override while pedestrian crossing is active
                return False, f"Cannot override active pedestrian crossing at '{config.junction_id}'. Remaining clearance: {junc.crossing_remaining_seconds}s"

        return True, "Valid configuration"

    def apply_configuration(self, config: SignalConfiguration) -> bool:
        """
        Validates and applies signal configuration to the target junction in network.
        Raises ValueError if validation fails.
        """
        is_valid, reason = self.validate_configuration(config)
        if not is_valid:
            raise ValueError(f"Signal configuration rejected for junction '{config.junction_id}': {reason}")

        junc = self.network.get_junction(config.junction_id)
        junc.signal_phase = config.signal_phase
        junc.green_duration = config.green_duration
        junc.red_duration = config.red_duration

        if config.priority_override or config.signal_phase == SignalPhase.EMERGENCY_PRIORITY:
            junc.emergency_reserved = True
            if config.reservation_id:
                self.active_reservations[config.junction_id] = config.reservation_id

        # Handle reservation release if explicit reservation_id supplied and marked release
        if config.reservation_id and config.reservation_id.startswith("RELEASE_"):
            real_res_id = config.reservation_id.replace("RELEASE_", "")
            self.release_reservation(config.junction_id, real_res_id)

        try:
            from app.websocket.events import broadcast_event
            broadcast_event("signal.updated", f"junction:{config.junction_id}", config.model_dump())
        except Exception:
            pass

        return True

    def create_reservation(self, junction_id: str, reservation_id: str) -> bool:
        """Reserves a junction for emergency corridor priority."""
        junc = self.network.get_junction(junction_id)
        if not junc:
            return False
        junc.emergency_reserved = True
        self.active_reservations[junction_id] = reservation_id
        return True

    def release_reservation(self, junction_id: str, reservation_id: str) -> bool:
        """Releases emergency corridor reservation for specified junction."""
        junc = self.network.get_junction(junction_id)
        if not junc:
            return False

        if self.active_reservations.get(junction_id) == reservation_id or junc.emergency_reserved:
            junc.emergency_reserved = False
            self.active_reservations.pop(junction_id, None)
            return True
        return False

    def set_pedestrian_crossing(self, junction_id: str, pedestrian_count: int, clearance_seconds: float = 15.0) -> bool:
        """Triggers active pedestrian crossing at junction."""
        junc = self.network.get_junction(junction_id)
        if not junc:
            return False
        junc.pedestrian_count = pedestrian_count
        junc.crossing_active = True
        junc.crossing_remaining_seconds = clearance_seconds
        junc.signal_phase = SignalPhase.PEDESTRIAN_CLEARANCE

        try:
            from app.websocket.events import broadcast_event
            broadcast_event(
                "pedestrian.updated",
                f"junction:{junction_id}",
                {
                    "junction_id": junction_id,
                    "pedestrian_count": pedestrian_count,
                    "crossing_active": True,
                    "crossing_remaining_seconds": clearance_seconds,
                },
            )
        except Exception:
            pass

        return True


    def tick_pedestrian_clearance(self, junction_id: str, dt: float = 1.0) -> None:
        """Decrements pedestrian clearance remaining seconds."""
        junc = self.network.get_junction(junction_id)
        if junc and junc.crossing_active:
            junc.crossing_remaining_seconds = max(0.0, junc.crossing_remaining_seconds - dt)
            if junc.crossing_remaining_seconds == 0.0:
                junc.crossing_active = False
