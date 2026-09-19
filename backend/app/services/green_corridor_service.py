import time
from typing import Dict, List, Optional, Set
from app.models.emergency import EmergencyAssignment
from app.models.green_corridor import CorridorStatus, GreenCorridorPlan, JunctionPriorityPlan
from app.models.signal import SignalConfiguration, SignalPhase
from app.simulation.network import TrafficNetwork
from app.simulation.signal_engine import SignalController


class GreenCorridorService:
    """
    Green Corridor Decision & Lifecycle Service (Backend Developer 2 Phase 5).
    Determines emergency signal priority plans for junctions along active emergency routes,
    enforces pedestrian clearance locks and conflict safety validation, and manages
    PLAN -> ACTIVATE -> RELEASE lifecycle transitions via Backend Developer 1's SignalController.
    """

    def __init__(self, signal_controller: SignalController, network: TrafficNetwork):
        self.signal_controller = signal_controller
        self.network = network
        self.active_plans: Dict[str, GreenCorridorPlan] = {}  # request_id -> GreenCorridorPlan

    def plan_corridor(self, assignment: EmergencyAssignment) -> GreenCorridorPlan:
        """
        Creates a structured Green Corridor priority plan for an EmergencyAssignment:
        1. Extracts ordered junction sequence from route path.
        2. Evaluates pedestrian clearance locks and signal conflict safety per junction.
        3. Prevents duplicate active corridor plans for the same request_id.
        """
        req_id = assignment.request_id
        route = assignment.route
        ordered_juncs = route.path

        if not ordered_juncs:
            raise ValueError(f"Assignment route for request '{req_id}' contains no junctions.")

        # Release existing active plan if present
        if req_id in self.active_plans and self.active_plans[req_id].status == CorridorStatus.ACTIVE:
            self.release_corridor(req_id)

        junction_plans: List[JunctionPriorityPlan] = []

        for idx, j_id in enumerate(ordered_juncs, start=1):
            junc = self.network.get_junction(j_id)
            if not junc:
                raise ValueError(f"Unknown junction ID: '{j_id}' in emergency route path.")

            # Safety Check 1: Pedestrian clearance active
            is_safe = True
            safety_reason: Optional[str] = None

            if junc.crossing_active and junc.crossing_remaining_seconds > 0:
                is_safe = False
                safety_reason = f"Active pedestrian crossing at junction '{j_id}' ({junc.crossing_remaining_seconds}s remaining)."
            else:
                # Safety Check 2: Signal Controller conflict validation
                test_config = SignalConfiguration(
                    junction_id=j_id,
                    signal_phase=SignalPhase.EMERGENCY_PRIORITY,
                    green_duration=60.0,
                    red_duration=15.0,
                    priority_override=True,
                )
                valid, reason = self.signal_controller.validate_configuration(test_config)
                if not valid:
                    is_safe = False
                    safety_reason = reason

            j_plan = JunctionPriorityPlan(
                junction_id=j_id,
                sequence_order=idx,
                requires_priority=True,
                requested_phase=SignalPhase.EMERGENCY_PRIORITY,
                green_duration=60.0,
                is_safe=is_safe,
                safety_reason=safety_reason,
                activated=False,
            )
            junction_plans.append(j_plan)

        corridor_id = f"CORRIDOR_{assignment.vehicle_id}_{req_id}"
        corridor_plan = GreenCorridorPlan(
            corridor_id=corridor_id,
            request_id=req_id,
            vehicle_id=assignment.vehicle_id,
            route_id=route.route_id,
            ordered_junctions=ordered_juncs,
            junction_plans=junction_plans,
            status=CorridorStatus.PLANNED,
            created_at=time.time(),
        )
        self.active_plans[req_id] = corridor_plan
        return corridor_plan

    def activate_corridor(self, request_id: str) -> GreenCorridorPlan:
        """
        Activates temporary emergency signal priority at safe junctions in the corridor plan
        and reserves junctions in SignalController.
        """
        if request_id not in self.active_plans:
            raise ValueError(f"No Green Corridor plan found for request '{request_id}'.")

        corridor = self.active_plans[request_id]

        for plan in corridor.junction_plans:
            if plan.is_safe:
                res_id = f"CORRIDOR_{corridor.corridor_id}"
                self.signal_controller.create_reservation(plan.junction_id, res_id)
                sig_config = SignalConfiguration(
                    junction_id=plan.junction_id,
                    signal_phase=SignalPhase.EMERGENCY_PRIORITY,
                    green_duration=plan.green_duration,
                    red_duration=15.0,
                    priority_override=True,
                    reservation_id=res_id,
                )
                self.signal_controller.apply_configuration(sig_config)
                plan.activated = True
            else:
                plan.activated = False

        corridor.status = CorridorStatus.ACTIVE
        return corridor

    def release_corridor(self, request_id: str) -> GreenCorridorPlan:
        """
        Releases emergency corridor signal priority and reservations across all corridor junctions,
        restoring baseline signal phase timing via SignalController.
        """
        if request_id not in self.active_plans:
            raise ValueError(f"No active Green Corridor plan found for request '{request_id}'.")

        corridor = self.active_plans[request_id]

        for plan in corridor.junction_plans:
            res_id = f"CORRIDOR_{corridor.corridor_id}"
            self.signal_controller.release_reservation(plan.junction_id, res_id)
            norm_config = SignalConfiguration(
                junction_id=plan.junction_id,
                signal_phase=SignalPhase.NS_GREEN,
                green_duration=30.0,
                red_duration=30.0,
                priority_override=False,
                reservation_id=f"RELEASE_{res_id}",
            )
            self.signal_controller.apply_configuration(norm_config)
            plan.activated = False

        corridor.status = CorridorStatus.RELEASED
        return self.active_plans.pop(request_id)

    def replan_corridor(self, new_assignment: EmergencyAssignment) -> GreenCorridorPlan:
        """
        Handles emergency rerouting by releasing junctions from old route no longer present
        in new_assignment, and creating/activating the updated Green Corridor plan.
        """
        req_id = new_assignment.request_id

        # 1. Release old junctions no longer present in new route path
        if req_id in self.active_plans:
            old_plan = self.active_plans[req_id]
            new_junc_set = set(new_assignment.route.path)
            res_id = f"CORRIDOR_{old_plan.corridor_id}"

            for plan in old_plan.junction_plans:
                if plan.junction_id not in new_junc_set:
                    self.signal_controller.release_reservation(plan.junction_id, res_id)
                    norm_config = SignalConfiguration(
                        junction_id=plan.junction_id,
                        signal_phase=SignalPhase.NS_GREEN,
                        green_duration=30.0,
                        red_duration=30.0,
                        priority_override=False,
                    )
                    self.signal_controller.apply_configuration(norm_config)

        # 2. Plan & activate new corridor
        new_plan = self.plan_corridor(new_assignment)
        activated_plan = self.activate_corridor(req_id)
        activated_plan.status = CorridorStatus.REROUTED
        return activated_plan
