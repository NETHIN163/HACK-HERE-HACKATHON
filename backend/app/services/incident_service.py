import time
from typing import Dict, List, Optional
from app.models.incident import Incident, IncidentType
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork


class IncidentService:
    """
    Service managing incident lifecycle (ACCIDENT, ROAD_CLOSURE).
    Updates road network statuses, triggers route impact events, and prepares WebSocket payloads.
    """

    def __init__(self, network: TrafficNetwork):
        self.network = network
        self.incidents: Dict[str, Incident] = {}
        self.event_queue: List[Dict] = []

    def _emit_event(self, event_type: str, data: Dict) -> None:
        """Stores structured event payload for later WebSocket broadcast."""
        event_payload = {
            "event": event_type,
            "data": data,
            "timestamp": time.time(),
        }
        self.event_queue.append(event_payload)

    def get_pending_events(self) -> List[Dict]:
        """Returns and clears all pending event payloads."""
        events = list(self.event_queue)
        self.event_queue.clear()
        return events

    def create_incident(
        self,
        incident_id: str,
        type: str,
        road_id: str,
        severity: float = 1.0,
        description: Optional[str] = None,
    ) -> Incident:
        """
        Creates a new incident on a specified road.
        
        Validates:
        - road_id exists in network
        - type is valid IncidentType (ACCIDENT, ROAD_CLOSURE)
        
        Actions:
        - Sets road status to BLOCKED (for ACCIDENT) or CLOSED (for ROAD_CLOSURE)
        - Emits 'incident.created' and 'route.impact_required' events
        """
        # 1. Validate road exists
        road = self.network.get_road(road_id)
        if not road:
            raise ValueError(f"Invalid road ID: '{road_id}' does not exist in network.")

        # 2. Validate incident type
        try:
            inc_type = IncidentType(type)
        except ValueError:
            raise ValueError(f"Invalid incident type: '{type}'. Must be ACCIDENT or ROAD_CLOSURE.")

        # 3. Check duplicate incident ID
        if incident_id in self.incidents:
            raise ValueError(f"Incident ID '{incident_id}' already exists.")

        # 4. Construct incident object
        incident = Incident(
            incident_id=incident_id,
            type=inc_type,
            road_id=road_id,
            severity=severity,
            description=description,
            timestamp=time.time(),
            active=True,
        )
        self.incidents[incident_id] = incident

        # 5. Update road status in network
        if inc_type == IncidentType.ACCIDENT:
            self.network.update_road_status(road_id, RoadStatus.BLOCKED)
        elif inc_type == IncidentType.ROAD_CLOSURE:
            self.network.update_road_status(road_id, RoadStatus.CLOSED)

        # 6. Emit events for WebSocket & system consumers
        self._emit_event("incident.created", incident.model_dump())
        self._emit_event(
            "route.impact_required",
            {
                "incident_id": incident_id,
                "road_id": road_id,
                "status": self.network.get_road(road_id).status,
            },
        )

        # Broadcast real-time WebSocket events
        try:
            from app.websocket.events import broadcast_event
            broadcast_event("incident.created", f"incident:{incident_id}", incident.model_dump())
            broadcast_event("route.impact_required", f"road:{road_id}", {"incident_id": incident_id, "status": road.status})
        except Exception:
            pass

        return incident


    def update_incident(
        self,
        incident_id: str,
        active: Optional[bool] = None,
        severity: Optional[float] = None,
        description: Optional[str] = None,
    ) -> Incident:
        """
        Updates an existing incident.
        If active is set to False (resolved), restores road status to OPEN if no other active incidents affect it.
        """
        if incident_id not in self.incidents:
            raise ValueError(f"Incident with ID '{incident_id}' not found.")

        incident = self.incidents[incident_id]

        if active is not None:
            incident.active = active
        if severity is not None:
            incident.severity = severity
        if description is not None:
            incident.description = description

        # If incident resolved (active=False), check if road should be restored to OPEN
        if active is False:
            other_active = any(
                inc.active and inc.road_id == incident.road_id and inc.incident_id != incident_id
                for inc in self.incidents.values()
            )
            if not other_active:
                self.network.update_road_status(incident.road_id, RoadStatus.OPEN)

        # Emit update event
        self._emit_event("incident.updated", incident.model_dump())
        self._emit_event(
            "route.impact_required",
            {
                "incident_id": incident_id,
                "road_id": incident.road_id,
                "status": self.network.get_road(incident.road_id).status,
            },
        )

        try:
            from app.websocket.events import broadcast_event
            broadcast_event("incident.updated", f"incident:{incident_id}", incident.model_dump())
        except Exception:
            pass

        return incident


    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Retrieves incident by ID."""
        return self.incidents.get(incident_id)

    def get_all_incidents(self, active_only: bool = False) -> List[Incident]:
        """Returns list of incidents."""
        if active_only:
            return [inc for inc in self.incidents.values() if inc.active]
        return list(self.incidents.values())
