from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field
from app.models.emergency import EmergencyRoute



class QUBOVariable(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    var_id: str = Field(..., description="Binary variable identifier (e.g. x_0, x_1)")
    route_id: str = Field(..., description="Associated emergency route ID")
    origin: str = Field(..., description="Route origin junction ID")
    destination: str = Field(..., description="Route destination junction ID")
    path: List[str] = Field(..., description="Sequence of junction IDs")
    travel_time: float = Field(..., description="Estimated route travel time in seconds")
    is_eligible: bool = Field(True, description="Whether route is eligible (contains no BLOCKED/CLOSED roads)")


class QUBOFormulation(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    variables: List[QUBOVariable] = Field(..., description="List of QUBO binary decision variables")
    q_matrix: Dict[str, float] = Field(..., description="QUBO upper-triangular coefficient matrix keyed by 'var1,var2'")
    var_to_route: Dict[str, EmergencyRoute] = Field(..., description="Map of binary variable ID to EmergencyRoute model")
    penalty_weight: float = Field(1000.0, description="Constraint penalty weight P for route selection constraint")
    linear_terms: Dict[str, float] = Field(default_factory=dict, description="Diagonal linear coefficients Q_ii")
    quadratic_terms: Dict[str, float] = Field(default_factory=dict, description="Off-diagonal quadratic coefficients Q_ij")


class QAOAResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    selected_route: Optional[EmergencyRoute] = Field(None, description="Decoded EmergencyRoute selected by QAOA/QUBO optimization")
    selected_variable: Optional[str] = Field(None, description="ID of active binary variable (e.g. x_0)")
    qubo_cost: float = Field(..., description="Energy cost H(x) of selected solution")
    is_valid: bool = Field(True, description="Whether selected route is feasible and eligible")
    execution_method: str = Field("SIMULATED_QAOA", description="Execution algorithm mode: SIMULATED_QAOA or EXACT_QUBO_SOLVER")
    candidate_evaluations: Dict[str, float] = Field(default_factory=dict, description="Map of variable ID to energy cost H(x)")
    optimal_binary_vector: Dict[str, int] = Field(default_factory=dict, description="Binary solution vector {x_0: 1, x_1: 0}")

