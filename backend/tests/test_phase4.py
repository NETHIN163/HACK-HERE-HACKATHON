import pytest
from app.models.signal import SignalConfiguration, SignalPhase
from app.simulation.network import TrafficNetwork
from app.simulation.traffic_engine import TrafficEngine
from app.simulation.signal_engine import SignalController
from app.optimization.classical import ClassicalOptimizer


def test_low_traffic_keeps_normal_signal_timing():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)
    optimizer = ClassicalOptimizer(base_green=30.0, base_red=30.0)

    # Empty/low traffic state
    state = engine.step(demands=[], dt=1.0)
    configs = optimizer.optimize(state)

    for j_id, config in configs.items():
        assert config.green_duration == 30.0
        assert config.red_duration == 30.0
        assert config.priority_override is False


def test_high_queue_increases_green_duration():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)
    optimizer = ClassicalOptimizer(queue_threshold=5, base_green=30.0)

    state = engine.step(demands=[], dt=1.0)
    # Set high queue on junction J1 state
    state.junctions["J1"].queue_length = 25

    configs = optimizer.optimize(state)
    j1_config = configs["J1"]
    assert j1_config.green_duration > 30.0  # Increased green duration due to queue


def test_high_congestion_receives_additional_green_time():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)
    optimizer = ClassicalOptimizer(congestion_threshold=0.5, base_green=30.0)

    state = engine.step(demands=[], dt=1.0)
    # Set high density on junction J2 state
    state.junctions["J2"].vehicle_density = 0.85

    configs = optimizer.optimize(state)
    j2_config = configs["J2"]
    assert j2_config.green_duration >= 50.0  # Base 30s + 20s congestion bonus



def test_emergency_priority_creates_safe_priority_phase():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)
    optimizer = ClassicalOptimizer()

    # Priority requested for J3
    state = engine.step(demands=[], dt=1.0)
    configs = optimizer.optimize(state, priority_requests={"J3": "RES_AMB_001"})

    j3_config = configs["J3"]
    assert j3_config.signal_phase == SignalPhase.EMERGENCY_PRIORITY
    assert j3_config.priority_override is True
    assert j3_config.reservation_id == "RES_AMB_001"


def test_invalid_and_conflicting_signal_movements_rejected():
    net = TrafficNetwork()
    controller = SignalController(network=net)

    # Unknown junction ID
    invalid_junc_config = SignalConfiguration(
        junction_id="J999",
        signal_phase=SignalPhase.NS_GREEN,
        green_duration=30.0,
        red_duration=30.0,
    )
    with pytest.raises(ValueError, match="Unknown junction ID"):
        controller.apply_configuration(invalid_junc_config)

    # Invalid green duration < 5 seconds rejected by Pydantic validation
    from pydantic import ValidationError
    with pytest.raises((ValueError, ValidationError)):
        SignalConfiguration(
            junction_id="J1",
            signal_phase=SignalPhase.NS_GREEN,
            green_duration=2.0,
            red_duration=30.0,
        )



def test_valid_signal_configurations_accepted():
    net = TrafficNetwork()
    controller = SignalController(network=net)

    valid_config = SignalConfiguration(
        junction_id="J1",
        signal_phase=SignalPhase.EW_GREEN,
        green_duration=45.0,
        red_duration=20.0,
    )

    success = controller.apply_configuration(valid_config)
    assert success is True

    j1 = net.get_junction("J1")
    assert j1.signal_phase == SignalPhase.EW_GREEN
    assert j1.green_duration == 45.0
    assert j1.red_duration == 20.0


def test_active_pedestrian_crossing_respected():
    net = TrafficNetwork()
    controller = SignalController(network=net)

    # Activate pedestrian crossing at J1
    controller.set_pedestrian_crossing("J1", pedestrian_count=10, clearance_seconds=15.0)

    # Attempt to switch to NS_GREEN while crossing is active
    override_config = SignalConfiguration(
        junction_id="J1",
        signal_phase=SignalPhase.NS_GREEN,
        green_duration=30.0,
        red_duration=30.0,
    )

    with pytest.raises(ValueError, match="Cannot override active pedestrian crossing"):
        controller.apply_configuration(override_config)


def test_pedestrian_clearance_state_works_correctly():
    net = TrafficNetwork()
    controller = SignalController(network=net)

    controller.set_pedestrian_crossing("J1", pedestrian_count=5, clearance_seconds=2.0)
    j1 = net.get_junction("J1")
    assert j1.crossing_active is True
    assert j1.signal_phase == SignalPhase.PEDESTRIAN_CLEARANCE

    # Tick clearance time
    controller.tick_pedestrian_clearance("J1", dt=1.0)
    assert j1.crossing_remaining_seconds == 1.0
    assert j1.crossing_active is True

    # Tick past remaining clearance time
    controller.tick_pedestrian_clearance("J1", dt=1.5)
    assert j1.crossing_remaining_seconds == 0.0
    assert j1.crossing_active is False

    # Now valid configuration can be applied
    new_config = SignalConfiguration(
        junction_id="J1",
        signal_phase=SignalPhase.NS_GREEN,
        green_duration=30.0,
        red_duration=30.0,
    )
    assert controller.apply_configuration(new_config) is True


def test_reservation_creation_and_release():
    net = TrafficNetwork()
    controller = SignalController(network=net)

    # Create reservation
    assert controller.create_reservation("J4", "AMB_CORRIDOR_1") is True
    j4 = net.get_junction("J4")
    assert j4.emergency_reserved is True
    assert controller.active_reservations.get("J4") == "AMB_CORRIDOR_1"

    # Release reservation
    assert controller.release_reservation("J4", "AMB_CORRIDOR_1") is True
    assert j4.emergency_reserved is False
    assert "J4" not in controller.active_reservations


def test_classical_optimizer_produces_deterministic_output():
    net1 = TrafficNetwork()
    engine1 = TrafficEngine(network=net1, seed=42)
    opt1 = ClassicalOptimizer()

    net2 = TrafficNetwork()
    engine2 = TrafficEngine(network=net2, seed=42)
    opt2 = ClassicalOptimizer()

    state1 = engine1.step(demands=[], dt=1.0)
    state2 = engine2.step(demands=[], dt=1.0)

    configs1 = opt1.optimize(state1)
    configs2 = opt2.optimize(state2)

    assert len(configs1) == len(configs2)
    for j_id in configs1:
        c1 = configs1[j_id]
        c2 = configs2[j_id]
        assert c1.signal_phase == c2.signal_phase
        assert c1.green_duration == c2.green_duration
        assert c1.red_duration == c2.red_duration
        assert c1.priority_override == c2.priority_override
