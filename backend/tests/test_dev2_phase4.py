import pytest
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork
from app.services.incident_service import IncidentService
from app.optimization.qubo_formulation import QUBOFormulationService
from app.optimization.qaoa_execution import QAOAExecutionService


def test_qaoa_service_accepts_valid_qubo_and_produces_solution():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)
    qaoa_service = QAOAExecutionService(method="SIMULATED_QAOA")

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")
    result = qaoa_service.execute_qaoa(formulation)

    assert result.is_valid is True
    assert result.selected_route is not None
    assert result.selected_variable is not None
    assert result.execution_method == "SIMULATED_QAOA"


def test_lowest_cost_valid_route_is_selected():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)
    qaoa_service = QAOAExecutionService()

    # Increase travel time on default path J1->J2->J3 road R_J1_J2 to 150s
    net.get_road("R_J1_J2").travel_time = 150.0

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")
    result = qaoa_service.execute_qaoa(formulation)

    assert result.is_valid is True
    # Should select faster alternate route (e.g. J1->J4->J5->J6->J3)
    assert result.selected_route.path != ["J1", "J2", "J3"]
    assert result.selected_route.estimated_travel_time < 150.0


def test_exactly_one_route_constraint_respected():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)
    qaoa_service = QAOAExecutionService()

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")

    # Evaluate invalid multi-route binary solution vector {x_0: 1, x_1: 1}
    multi_vector = {"x_0": 1, "x_1": 1, "x_2": 0}
    energy_multi = qaoa_service.evaluate_qubo_energy(formulation, multi_vector)

    # Evaluate 1-hot binary solution vector {x_0: 1, x_1: 0}
    single_vector = {"x_0": 1, "x_1": 0, "x_2": 0}
    energy_single = qaoa_service.evaluate_qubo_energy(formulation, single_vector)

    # Multi-selection energy must be significantly higher due to P*(sum x_i - 1)^2 penalty
    assert energy_multi > energy_single


def test_blocked_and_closed_routes_cannot_be_selected():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    qubo_service = QUBOFormulationService(network=net)
    qaoa_service = QAOAExecutionService()

    # Block direct route R_J1_J2
    inc_service.create_incident("INC_1", "ACCIDENT", "R_J1_J2")

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")
    result = qaoa_service.execute_qaoa(formulation)

    assert result.is_valid is True
    # Selected route must not contain blocked road R_J1_J2
    assert "R_J1_J2" not in result.selected_route.road_ids


def test_selected_qubo_variable_maps_to_correct_emergency_route():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)
    qaoa_service = QAOAExecutionService()

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")
    result = qaoa_service.execute_qaoa(formulation)

    selected_var_id = result.selected_variable
    mapped_route = formulation.var_to_route[selected_var_id]

    assert result.selected_route.route_id == mapped_route.route_id
    assert result.selected_route.path == mapped_route.path


def test_deterministic_execution_and_stable_tie_breaking():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)
    qaoa_service = QAOAExecutionService()

    formulation1 = qubo_service.build_qubo_for_request(origin="J1", destination="J3")
    res1 = qaoa_service.execute_qaoa(formulation1)

    formulation2 = qubo_service.build_qubo_for_request(origin="J1", destination="J3")
    res2 = qaoa_service.execute_qaoa(formulation2)

    assert res1.selected_variable == res2.selected_variable
    assert res1.qubo_cost == res2.qubo_cost
    assert res1.selected_route.path == res2.selected_route.path


def test_empty_and_invalid_qubo_handling():
    qaoa_service = QAOAExecutionService()

    # None formulation
    res_none = qaoa_service.execute_qaoa(None)
    assert res_none.is_valid is False
    assert res_none.selected_route is None

    # Empty formulation
    from app.models.qubo import QUBOFormulation
    empty_formulation = QUBOFormulation(variables=[], q_matrix={}, var_to_route={})
    res_empty = qaoa_service.execute_qaoa(empty_formulation)
    assert res_empty.is_valid is False
    assert res_empty.selected_route is None


def test_no_feasible_solution_when_all_routes_blocked():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    qubo_service = QUBOFormulationService(network=net)
    qaoa_service = QAOAExecutionService()

    # Block all outbound roads from J1: R_J1_J2 and R_J1_J4
    inc_service.create_incident("INC_1", "ACCIDENT", "R_J1_J2")
    inc_service.create_incident("INC_2", "ROAD_CLOSURE", "R_J1_J4")

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")
    result = qaoa_service.execute_qaoa(formulation)

    assert result.is_valid is False
    assert result.selected_route is None


def test_simulated_qaoa_fallback_execution_mode():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)
    qaoa_service = QAOAExecutionService(method="SIMULATED_QAOA")

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")
    result = qaoa_service.execute_qaoa(formulation)

    assert result.execution_method == "SIMULATED_QAOA"
    assert result.is_valid is True
