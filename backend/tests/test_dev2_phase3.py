import pytest
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork
from app.services.incident_service import IncidentService
from app.services.emergency_routing_service import EmergencyRoutingService
from app.optimization.qubo_formulation import QUBOFormulationService


def test_qubo_variable_creation():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")

    assert len(formulation.variables) > 0
    var0 = formulation.variables[0]
    assert var0.var_id == "x_0"
    assert var0.origin == "J1"
    assert var0.destination == "J3"
    assert var0.is_eligible is True


def test_candidate_route_to_binary_variable_mapping():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")

    for var in formulation.variables:
        assert var.var_id in formulation.var_to_route
        route = formulation.var_to_route[var.var_id]
        assert route.path == var.path


def test_route_cost_travel_time_objective():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3", penalty_weight=1000.0)

    # Q_00 = c_0 - P = travel_time - 1000.0
    var0 = formulation.variables[0]
    expected_linear = round(var0.travel_time - 1000.0, 4)
    assert formulation.q_matrix["x_0,x_0"] == expected_linear


def test_route_selection_constraint_quadratic_penalty():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3", penalty_weight=1000.0)

    # Off-diagonal quadratic penalty Q_01 = 2 * P = 2000.0
    if "x_0,x_1" in formulation.q_matrix:
        assert formulation.q_matrix["x_0,x_1"] == 2000.0


def test_penalty_for_ineligible_blocked_and_closed_routes():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    qubo_service = QUBOFormulationService(network=net)

    # Block R_J1_J2 with an accident
    inc_service.create_incident("INC_1", "ACCIDENT", "R_J1_J2")

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3", penalty_weight=1000.0)

    # Route traversing R_J1_J2 should be marked ineligible and have higher linear penalty Q_kk
    ineligible_var = next(v for v in formulation.variables if "J2" in v.path)
    assert ineligible_var.is_eligible is False

    # Linear term for ineligible variable includes ineligible_penalty +10000.0
    q_key = f"{ineligible_var.var_id},{ineligible_var.var_id}"
    assert formulation.q_matrix[q_key] > 5000.0


def test_closed_road_exclusion_in_qubo():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    qubo_service = QUBOFormulationService(network=net)

    # Close R_J1_J2
    inc_service.create_incident("INC_CLS", "ROAD_CLOSURE", "R_J1_J2")

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")

    var_j2 = next(v for v in formulation.variables if "J2" in v.path)
    assert var_j2.is_eligible is False


def test_multiple_candidate_routes():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")

    # J1 to J3 has multiple simple paths e.g. J1->J2->J3, J1->J4->J5->J6->J3, J1->J2->J5->J6->J3
    assert len(formulation.variables) >= 3


def test_deterministic_qubo_output():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)

    f1 = qubo_service.build_qubo_for_request(origin="J1", destination="J3")
    f2 = qubo_service.build_qubo_for_request(origin="J1", destination="J3")

    assert len(f1.variables) == len(f2.variables)
    assert f1.q_matrix == f2.q_matrix


def test_selected_variable_decodes_back_to_original_route():
    net = TrafficNetwork()
    routing_service = EmergencyRoutingService(network=net)
    qubo_service = QUBOFormulationService(network=net)

    formulation = qubo_service.build_qubo_for_request(origin="J1", destination="J3")

    # Binary solution picking x_0 (shortest path J1->J2->J3)
    solution = {"x_0": 1, "x_1": 0, "x_2": 0}

    decoded_route = qubo_service.decode_solution(formulation, solution)
    assert decoded_route is not None
    assert decoded_route.origin == "J1"
    assert decoded_route.destination == "J3"
    assert decoded_route.path == formulation.variables[0].path


def test_empty_no_route_and_invalid_input_handling():
    net = TrafficNetwork()
    qubo_service = QUBOFormulationService(network=net)

    # Empty candidate routes list
    with pytest.raises(ValueError, match="No candidate routes provided"):
        qubo_service.build_qubo_from_routes([])

    # Invalid origin / destination junction IDs
    with pytest.raises(ValueError, match="Invalid origin"):
        qubo_service.build_qubo_for_request(origin="J_INVALID", destination="J3")
