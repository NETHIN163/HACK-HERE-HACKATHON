from typing import Dict, List, Optional, Tuple
from app.models.qubo import QAOAResult, QUBOFormulation
from app.models.emergency import EmergencyRoute


class QAOAExecutionService:
    """
    QAOA Execution Service for Emergency Route Selection (Backend Developer 2 Phase 4).
    Consumes the QUBO formulation from Phase 3 and evaluates candidate binary solutions
    to identify the lowest-cost feasible emergency route.
    
    Provides a deterministic simulated/classical QAOA execution layer suitable for production MVP
    without requiring external quantum hardware.
    """

    def __init__(self, method: str = "SIMULATED_QAOA"):
        self.method = method

    def evaluate_qubo_energy(
        self,
        formulation: QUBOFormulation,
        binary_vector: Dict[str, int],
    ) -> float:
        """
        Calculates exact energy cost H(x) = x^T Q x for a given binary solution vector.
        Includes linear diagonal terms, quadratic off-diagonal terms, and constraint penalties.
        """
        energy = 0.0

        # Linear terms Q_ii * x_i
        for var_id, val in binary_vector.items():
            if val == 1:
                key_linear = f"{var_id},{var_id}"
                if key_linear in formulation.q_matrix:
                    energy += formulation.q_matrix[key_linear]

        # Quadratic terms Q_ij * x_i * x_j
        var_ids = sorted(list(binary_vector.keys()))
        N = len(var_ids)
        for i in range(N):
            for j in range(i + 1, N):
                v_i, v_j = var_ids[i], var_ids[j]
                if binary_vector.get(v_i, 0) == 1 and binary_vector.get(v_j, 0) == 1:
                    key_quad = f"{v_i},{v_j}"
                    if key_quad in formulation.q_matrix:
                        energy += formulation.q_matrix[key_quad]

        # Single selection constraint penalty: P * (sum x_i - 1)^2
        active_count = sum(binary_vector.values())
        if active_count != 1:
            energy += formulation.penalty_weight * ((active_count - 1) ** 2)

        return round(energy, 4)

    def execute_qaoa(self, formulation: Optional[QUBOFormulation]) -> QAOAResult:
        """
        Consumes a QUBO formulation and identifies the optimal binary decision variable.
        Returns a structured QAOAResult containing the selected EmergencyRoute.
        
        Rules:
        1. Consumes QUBO representation directly from Phase 3.
        2. Evaluates candidate binary 1-hot solutions x_k = 1.
        3. Rejects/penalizes BLOCKED or CLOSED routes.
        4. Applies stable tie-breaking for deterministic output.
        5. Maps selected variable back to the original EmergencyRoute model.
        """
        # 1. Validation for empty / invalid QUBO
        if not formulation or not formulation.variables or not formulation.q_matrix:
            return QAOAResult(
                selected_route=None,
                selected_variable=None,
                qubo_cost=999999.0,
                is_valid=False,
                execution_method=self.method,
                candidate_evaluations={},
                optimal_binary_vector={},
            )

        candidate_evaluations: Dict[str, float] = {}

        # Tuple: (is_eligible, energy_cost, var_id, route)
        candidates: List[Tuple[bool, float, str, EmergencyRoute]] = []

        # 2. Evaluate 1-hot candidate solutions x_k = 1
        for var_obj in formulation.variables:
            var_id = var_obj.var_id
            
            # Build 1-hot binary vector
            binary_vec = {v.var_id: (1 if v.var_id == var_id else 0) for v in formulation.variables}
            
            # Compute QUBO energy cost H(x)
            energy = self.evaluate_qubo_energy(formulation, binary_vec)
            candidate_evaluations[var_id] = energy

            route = formulation.var_to_route.get(var_id)
            if route:
                candidates.append((var_obj.is_eligible, energy, var_id, route))

        # Filter out ineligible routes (routes with BLOCKED/CLOSED roads)
        eligible_candidates = [c for c in candidates if c[0]]

        if not eligible_candidates:
            # All candidate routes are blocked or closed
            return QAOAResult(
                selected_route=None,
                selected_variable=None,
                qubo_cost=999999.0,
                is_valid=False,
                execution_method=self.method,
                candidate_evaluations=candidate_evaluations,
                optimal_binary_vector={},
            )

        # 3. Deterministic Sorting
        # Sort key: (energy_cost, var_id)
        # Lowest QUBO energy cost first; stable tie-breaking on var_id string
        eligible_candidates.sort(key=lambda c: (c[1], c[2]))
        best_candidate = eligible_candidates[0]

        is_eligible, best_cost, best_var_id, best_route = best_candidate

        # 4. Construct Optimal Binary Vector
        optimal_vector = {v.var_id: (1 if v.var_id == best_var_id else 0) for v in formulation.variables}

        # 5. Return QAOAResult with mapped EmergencyRoute
        return QAOAResult(
            selected_route=best_route,
            selected_variable=best_var_id,
            qubo_cost=best_cost,
            is_valid=True,
            execution_method=self.method,
            candidate_evaluations=candidate_evaluations,
            optimal_binary_vector=optimal_vector,
        )
