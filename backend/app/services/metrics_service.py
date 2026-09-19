from typing import Dict, List, Optional
from app.models.traffic import TrafficState
from app.models.metrics import TrafficMetrics
from app.simulation.traffic_engine import TrafficEngine


class MetricsService:
    """
    Reusable Metrics Calculator.
    Evaluates traffic states under Classical, Hybrid, or raw simulation runs.
    Calculates queue lengths, travel times, throughput, environmental impact, and pedestrian delays.
    """

    @staticmethod
    def calculate_metrics(
        traffic_state: TrafficState,
        engine: Optional[TrafficEngine] = None,
        emergency_route: Optional[List[str]] = None,
    ) -> TrafficMetrics:
        """
        Calculates standardized TrafficMetrics from TrafficState snapshot and optional engine runtime stats.
        """
        roads = list(traffic_state.roads.values())
        junctions = list(traffic_state.junctions.values())

        num_roads = max(1, len(roads))

        # 1. Average & Maximum Queue Length
        total_road_queue = sum(r.queue_length for r in roads)
        total_junc_queue = sum(j.queue_length for j in junctions)
        avg_queue = round(total_road_queue / num_roads, 2)

        max_queue_road = max((r.queue_length for r in roads), default=0)
        max_queue_junc = max((j.queue_length for j in junctions), default=0)
        max_queue = max(max_queue_road, max_queue_junc)

        # 2. Average Waiting Time
        if engine and hasattr(engine, "road_waiting_times"):
            total_wait = sum(engine.road_waiting_times.values())
            avg_wait = round(total_wait / num_roads, 2)
        else:
            # Estimate waiting time from queue lengths (approx 2s wait per queued vehicle)
            avg_wait = round(avg_queue * 2.5, 2)

        # 3. Traffic Throughput
        if engine and hasattr(engine, "road_flows"):
            throughput = round(sum(engine.road_flows.values()), 2)
        else:
            # Estimate throughput from density and capacity
            throughput = round(sum(r.capacity * (1.0 - r.traffic_density) for r in roads if r.status in ["OPEN", "CONGESTED"]), 2)

        # 4. Emergency Route Metrics
        default_route = emergency_route or ["R_J1_J2", "R_J2_J3"]
        emerg_travel_time = 0.0
        emerg_free_flow_time = 0.0

        for r_id in default_route:
            if r_id in traffic_state.roads:
                r = traffic_state.roads[r_id]
                emerg_travel_time += r.travel_time
                emerg_free_flow_time += r.distance / 13.89  # 50 km/h free flow

        emerg_travel_time = round(emerg_travel_time, 2)
        emerg_delay = round(max(0.0, emerg_travel_time - emerg_free_flow_time), 2)

        # 5. Environmental Fuel & CO2 Estimates
        # Fuel consumption formula:
        # Base idling/cruising: 0.04 Liters/min per active vehicle density unit
        # Queue acceleration penalty: 0.01 Liters per queued vehicle
        total_density = sum(r.traffic_density for r in roads)
        fuel = round(total_density * 1.2 + total_road_queue * 0.05 + 0.5, 2)
        co2 = round(fuel * 2.31, 2)  # 2.31 kg CO2 per Liter petrol

        # 6. Pedestrian Delay
        ped_delay = 0.0
        for j in junctions:
            ped_delay += j.pedestrian_count * 5.0 + j.crossing_remaining_seconds
        ped_delay = round(ped_delay, 2)

        return TrafficMetrics(
            average_waiting_time=avg_wait,
            average_queue_length=avg_queue,
            maximum_queue_length=max_queue,
            traffic_throughput=throughput,
            emergency_delay=emerg_delay,
            emergency_travel_time=emerg_travel_time,
            fuel_estimate=fuel,
            co2_estimate=co2,
            pedestrian_delay=ped_delay,
        )
