import time
from typing import Dict, List, Optional, Set, Tuple
from app.models.emergency import EmergencyAssignment, EmergencyPriority, EmergencyRequest
from app.models.emergency_conflict import ConflictStatus, EmergencyConflictResult, JunctionConflict
from app.simulation.network import TrafficNetwork
from app.simulation.signal_engine import SignalController
from app.services.green_corridor_service import GreenCorridorService


class EmergencyConflictResolutionService:
    """
    Emergency Conflict Resolution Service (Backend Developer 2 Phase 6).
    Detects and resolves priority conflicts when multiple emergency vehicles request overlapping
    junctions or road segments simultaneously.
    
    Resolution Policy:
    1. Emergency Priority Rating (CRITICAL > HIGH > MEDIUM > LOW)
    2. Estimated Route Travel Time (Shorter travel time receives priority)
    3. Request Timestamp (Earlier timestamp receives priority)
    4. Stable Request ID string sorting for deterministic tie-breaking.
    
    Safety:
    - Never bypasses pedestrian clearance locks or signal movement conflicts.
    - If a junction cannot safely receive priority, defers priority and maintains safe baseline state.
    """

    PRIORITY_RANK: Dict[str, int] = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    def __init__(
        self,
        green_corridor_service: GreenCorridorService,
        signal_controller: SignalController,
        network: TrafficNetwork,
    ):
        self.green_corridor_service = green_corridor_service
        self.signal_controller = signal_controller
        self.network = network

    def detect_conflicts(
        self,
        assignments: List[EmergencyAssignment],
    ) -> EmergencyConflictResult:
        """
        Detects overlapping junctions and road segments across active emergency assignments.
        """
        if not assignments or len(assignments) <= 1:
            return EmergencyConflictResult(
                conflict_id=f"CONF_DET_{int(time.time() * 1000) % 100000}",
                status=ConflictStatus.NO_CONFLICT,
                conflicting_request_ids=[a.request_id for a in assignments] if assignments else [],
                overlapping_junctions=[],
                overlapping_roads=[],
                junction_resolutions=[],
                granted_requests=[a.request_id for a in assignments] if assignments else [],
                deferred_requests=[],
                timestamp=time.time(),
            )

        # Map junction_id -> list of request_ids traversing it
        junc_map: Dict[str, List[str]] = {}
        # Map road_id -> list of request_ids traversing it
        road_map: Dict[str, List[str]] = {}

        for asg in assignments:
            req_id = asg.request_id
            for j_id in asg.route.path:
                junc_map.setdefault(j_id, []).append(req_id)
            for r_id in asg.route.road_ids:
                road_map.setdefault(r_id, []).append(req_id)

        overlapping_juncs = [j_id for j_id, reqs in junc_map.items() if len(reqs) > 1]
        overlapping_roads = [r_id for r_id, reqs in road_map.items() if len(reqs) > 1]

        conflicting_reqs = set()
        for j_id in overlapping_juncs:
            conflicting_reqs.update(junc_map[j_id])

        if not overlapping_juncs:
            return EmergencyConflictResult(
                conflict_id=f"CONF_DET_{int(time.time() * 1000) % 100000}",
                status=ConflictStatus.NO_CONFLICT,
                conflicting_request_ids=[],
                overlapping_junctions=[],
                overlapping_roads=overlapping_roads,
                junction_resolutions=[],
                granted_requests=[a.request_id for a in assignments],
                deferred_requests=[],
                timestamp=time.time(),
            )

        return EmergencyConflictResult(
            conflict_id=f"CONF_DET_{int(time.time() * 1000) % 100000}",
            status=ConflictStatus.DEFERRED,
            conflicting_request_ids=sorted(list(conflicting_reqs)),
            overlapping_junctions=sorted(overlapping_juncs),
            overlapping_roads=sorted(overlapping_roads),
            junction_resolutions=[],
            granted_requests=[],
            deferred_requests=[],
            timestamp=time.time(),
        )

    def resolve_conflicts(
        self,
        assignments: List[EmergencyAssignment],
        requests: Dict[str, EmergencyRequest],
    ) -> EmergencyConflictResult:
        """
        Detects and resolves emergency priority conflicts deterministically:
        1. Identifies competing requests for shared junctions.
        2. Evaluates pedestrian clearance locks.
        3. Ranks competing requests by Priority -> Travel Time -> Timestamp -> Request ID.
        4. Grants priority to winning request and defers losing requests at shared junctions.
        5. Updates GreenCorridor plans accordingly.
        """
        detection = self.detect_conflicts(assignments)
        if detection.status == ConflictStatus.NO_CONFLICT:
            # Grant all corridors
            granted = []
            for asg in assignments:
                self.green_corridor_service.plan_corridor(asg)
                self.green_corridor_service.activate_corridor(asg.request_id)
                granted.append(asg.request_id)

            return EmergencyConflictResult(
                conflict_id=f"CONF_RES_{int(time.time() * 1000) % 100000}",
                status=ConflictStatus.NO_CONFLICT,
                conflicting_request_ids=[],
                overlapping_junctions=[],
                overlapping_roads=detection.overlapping_roads,
                junction_resolutions=[],
                granted_requests=granted,
                deferred_requests=[],
                timestamp=time.time(),
            )

        # Map junction_id -> list of competing assignments
        competing_map: Dict[str, List[EmergencyAssignment]] = {}
        for asg in assignments:
            for j_id in asg.route.path:
                competing_map.setdefault(j_id, []).append(asg)

        junction_resolutions: List[JunctionConflict] = []
        granted_set: Set[str] = set()
        deferred_set: Set[str] = set()

        # Evaluate each overlapping junction
        for j_id in detection.overlapping_junctions:
            comp_asgs = competing_map[j_id]
            comp_req_ids = [a.request_id for a in comp_asgs]

            junc = self.network.get_junction(j_id)
            # Safety Check: Active pedestrian clearance at junction
            if junc and junc.crossing_active and junc.crossing_remaining_seconds > 0:
                # Defer ALL priority requests for this junction for safety
                j_conflict = JunctionConflict(
                    junction_id=j_id,
                    competing_request_ids=comp_req_ids,
                    winner_request_id=None,
                    deferred_request_ids=comp_req_ids,
                    resolution_reason=f"Pedestrian crossing active at junction '{j_id}' ({junc.crossing_remaining_seconds}s remaining). Emergency priority deferred for safety.",
                )
                junction_resolutions.append(j_conflict)
                deferred_set.update(comp_req_ids)
                continue

            # Deterministic Multi-Factor Ranking
            def sort_key(asg: EmergencyAssignment) -> Tuple[int, float, float, str]:
                req = requests.get(asg.request_id)
                p_val = req.priority.value if req and hasattr(req.priority, "value") else str(req.priority) if req else "HIGH"
                p_rank = self.PRIORITY_RANK.get(str(p_val).upper(), 3)
                t_time = asg.route.estimated_travel_time
                t_stamp = req.timestamp if req else 0.0
                return (p_rank, -t_time, -t_stamp, asg.request_id)

            sorted_asgs = sorted(comp_asgs, key=sort_key, reverse=True)
            winner_asg = sorted_asgs[0]
            winner_id = winner_asg.request_id
            deferred_ids = [a.request_id for a in sorted_asgs[1:]]

            granted_set.add(winner_id)
            deferred_set.update(deferred_ids)

            w_req = requests.get(winner_id)
            w_prio = w_req.priority if w_req else "HIGH"
            w_time = winner_asg.route.estimated_travel_time

            j_conflict = JunctionConflict(
                junction_id=j_id,
                competing_request_ids=comp_req_ids,
                winner_request_id=winner_id,
                deferred_request_ids=deferred_ids,
                resolution_reason=f"Request '{winner_id}' granted priority (Priority: {w_prio}, Travel Time: {w_time}s) over deferred requests {deferred_ids}.",
            )
            junction_resolutions.append(j_conflict)

        # Remove winners from deferred_set if they had no losses
        final_deferred = [r for r in sorted(list(deferred_set)) if r not in granted_set or any(jc.winner_request_id != r for jc in junction_resolutions if r in jc.competing_request_ids)]

        # Update GreenCorridor plans for all assignments
        for asg in assignments:
            req_id = asg.request_id
            corridor_plan = self.green_corridor_service.plan_corridor(asg)

            # If request was deferred at any junction, mark that junction unsafe in corridor plan
            for j_res in junction_resolutions:
                if req_id in j_res.deferred_request_ids:
                    for jp in corridor_plan.junction_plans:
                        if jp.junction_id == j_res.junction_id:
                            jp.is_safe = False
                            jp.safety_reason = j_res.resolution_reason

            # Activate corridor plan
            self.green_corridor_service.activate_corridor(req_id)

        return EmergencyConflictResult(
            conflict_id=f"CONF_RES_{int(time.time() * 1000) % 100000}",
            status=ConflictStatus.RESOLVED if junction_resolutions else ConflictStatus.NO_CONFLICT,
            conflicting_request_ids=detection.conflicting_request_ids,
            overlapping_junctions=detection.overlapping_junctions,
            overlapping_roads=detection.overlapping_roads,
            junction_resolutions=junction_resolutions,
            granted_requests=sorted(list(granted_set)),
            deferred_requests=sorted(list(final_deferred)),
            timestamp=time.time(),
        )

    def handle_corridor_release(
        self,
        released_request_id: str,
        remaining_assignments: List[EmergencyAssignment],
        requests: Dict[str, EmergencyRequest],
    ) -> EmergencyConflictResult:
        """
        Re-evaluates remaining active emergency assignments when an emergency request/corridor is released.
        Grants priority to previously deferred requests if their routes are now conflict-free.
        """
        if released_request_id in self.green_corridor_service.active_plans:
            self.green_corridor_service.release_corridor(released_request_id)

        if not remaining_assignments:
            return EmergencyConflictResult(
                conflict_id=f"CONF_REL_{int(time.time() * 1000) % 100000}",
                status=ConflictStatus.NO_CONFLICT,
                conflicting_request_ids=[],
                overlapping_junctions=[],
                overlapping_roads=[],
                junction_resolutions=[],
                granted_requests=[],
                deferred_requests=[],
                timestamp=time.time(),
            )

        return self.resolve_conflicts(remaining_assignments, requests)

    def handle_route_change(
        self,
        updated_assignment: EmergencyAssignment,
        active_assignments: List[EmergencyAssignment],
        requests: Dict[str, EmergencyRequest],
    ) -> EmergencyConflictResult:
        """
        Re-evaluates conflict detection and resolution when an emergency vehicle route changes.
        """
        # Replace or insert updated assignment in list
        filtered_asgs = [a for a in active_assignments if a.request_id != updated_assignment.request_id]
        filtered_asgs.append(updated_assignment)

        # Update corridor plan for rerouted vehicle
        self.green_corridor_service.replan_corridor(updated_assignment)

        return self.resolve_conflicts(filtered_asgs, requests)
