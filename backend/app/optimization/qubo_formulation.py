import time
from typing import Dict, List, Optional, Tuple
from app.models.emergency import EmergencyRoute, RouteStatus
from app.models.qubo import QUBOFormulation, QUBOVariable
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork


class QUBOFormulationService:
    """
    QUBO Formulation Service for Emergency Vehicle Routing (Backend Developer 2 Phase 3).
    Formulates route selection as a binary quadratic unconstrained optimization problem (QUBO).
    
    Mathematical Model:
        Min H(x) = sum_k (c_k * x_k) + P * (sum_k x_k - 1)^2 + sum_{k in ineligible} P_ineligible * x_k
    """

    def __init__(self, network: TrafficNetwork):
        self.network = network

    def build_qubo_from_routes(
        self,
        candidate_routes: List[EmergencyRoute],
        penalty_weight: float = 1000.0,
        ineligible_penalty: float = 10000.0,
    ) -> QUBOFormulation:
        """
        Builds a QUBO formulation from a list of candidate EmergencyRoute objects.
        
        Validates:
        - candidate_routes is non-empty
        - De-duplicates routes with identical path sequences
        
        Matrix Construction:
        - Diagonal Linear Q_kk = c_k - P + (P_ineligible if ineligible)
        - Off-Diagonal Quadratic Q_ij = 2 * P (for i < j)
        """
        if not candidate_routes:
            raise ValueError("No candidate routes provided for QUBO formulation.")

        # De-duplicate candidate routes based on junction path tuple
        unique_routes: List[EmergencyRoute] = []
        seen_paths = set()
        for route in candidate_routes:
            path_tuple = tuple(route.path)
            if path_tuple not in seen_paths:
                seen_paths.add(path_tuple)
                unique_routes.append(route)

        variables: List[QUBOVariable] = []
        var_to_route: Dict[str, EmergencyRoute] = {}
        linear_terms: Dict[str, float] = {}
        quadratic_terms: Dict[str, float] = {}
        q_matrix: Dict[str, float] = {}

        N = len(unique_routes)

        # 1. Create QUBO binary decision variables (x_0, x_1, ..., x_{N-1})
        for k, route in enumerate(unique_routes):
            var_id = f"x_{k}"
            
            # Verify eligibility: route must not contain any BLOCKED or CLOSED roads
            is_eligible = True
            for i in range(len(route.path) - 1):
                u, v = route.path[i], route.path[i + 1]
                road_id = f"R_{u}_{v}"
                road = self.network.get_road(road_id)
                if not road or road.status in [RoadStatus.BLOCKED, RoadStatus.CLOSED]:
                    is_eligible = False
                    break

            qubo_var = QUBOVariable(
                var_id=var_id,
                route_id=route.route_id,
                origin=route.origin,
                destination=route.destination,
                path=route.path,
                travel_time=route.estimated_travel_time,
                is_eligible=is_eligible,
            )
            variables.append(qubo_var)
            var_to_route[var_id] = route

            # Calculate Linear Coefficient Q_kk
            # H(x) expansion linear term: c_k - penalty_weight + (ineligible_penalty if not eligible)
            c_k = route.estimated_travel_time
            q_kk = c_k - penalty_weight
            if not is_eligible:
                q_kk += ineligible_penalty

            linear_terms[var_id] = round(q_kk, 4)
            q_matrix[f"{var_id},{var_id}"] = round(q_kk, 4)

        # 2. Calculate Quadratic Off-Diagonal Coupling Terms Q_ij = 2 * P (i < j)
        for i in range(N):
            for j in range(i + 1, N):
                var_i = f"x_{i}"
                var_j = f"x_{j}"
                q_ij = 2.0 * penalty_weight
                key = f"{var_i},{var_j}"
                quadratic_terms[key] = round(q_ij, 4)
                q_matrix[key] = round(q_ij, 4)

        return QUBOFormulation(
            variables=variables,
            q_matrix=q_matrix,
            var_to_route=var_to_route,
            penalty_weight=penalty_weight,
            linear_terms=linear_terms,
            quadratic_terms=quadratic_terms,
        )

    def build_qubo_for_request(
        self,
        origin: str,
        destination: str,
        penalty_weight: float = 1000.0,
    ) -> QUBOFormulation:
        """
        Generates candidate routes between origin and destination using NetworkX topology
        and builds the QUBO formulation.
        """
        if origin not in self.network.junctions:
            raise ValueError(f"Invalid origin junction ID: '{origin}'")
        if destination not in self.network.junctions:
            raise ValueError(f"Invalid destination junction ID: '{destination}'")

        # Find all simple paths between origin and destination (including paths with blocked roads)
        all_paths = self.network.find_all_paths(origin, destination, ignore_blocked=False)
        if not all_paths:
            raise ValueError(f"No topological paths exist between '{origin}' and '{destination}'.")

        candidate_routes: List[EmergencyRoute] = []
        for idx, path in enumerate(all_paths):
            road_ids = []
            total_dist = 0.0
            total_time = 0.0
            has_blocked = False

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                r_id = f"R_{u}_{v}"
                road = self.network.get_road(r_id)
                if not road or road.status in [RoadStatus.BLOCKED, RoadStatus.CLOSED]:
                    has_blocked = True
                    total_time += 999999.0
                    total_dist += 500.0
                else:
                    total_time += road.travel_time
                    total_dist += road.distance
                road_ids.append(r_id)

            route_status = RouteStatus.BLOCKED if has_blocked else RouteStatus.CALCULATED
            route = EmergencyRoute(
                route_id=f"CAND_ROUTE_{idx}_{origin}_{destination}",
                origin=origin,
                destination=destination,
                path=path,
                road_ids=road_ids,
                total_distance=round(total_dist, 2),
                estimated_travel_time=round(total_time, 2),
                status=route_status,
            )
            candidate_routes.append(route)

        return self.build_qubo_from_routes(
            candidate_routes=candidate_routes,
            penalty_weight=penalty_weight,
        )

    def decode_solution(
        self,
        formulation: QUBOFormulation,
        binary_solution: Dict[str, int],
    ) -> Optional[EmergencyRoute]:
        """
        Decodes a binary solution vector (e.g. {'x_0': 1, 'x_1': 0}) back to the corresponding EmergencyRoute.
        Validates route eligibility. Returns None if selected variable is ineligible or invalid.
        """
        active_vars = [var_id for var_id, val in binary_solution.items() if val == 1]

        if not active_vars:
            # No route selected in solution
            return None

        # Select first active binary variable
        selected_var_id = active_vars[0]
        if selected_var_id not in formulation.var_to_route:
            return None

        # Check corresponding variable eligibility
        var_obj = next((v for v in formulation.variables if v.var_id == selected_var_id), None)
        if var_obj and not var_obj.is_eligible:
            # Selected route is ineligible/blocked -> return None
            return None

        return formulation.var_to_route[selected_var_id]
