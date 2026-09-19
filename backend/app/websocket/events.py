import asyncio
import logging
import time
from typing import Any, Dict, List
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("qflow.websocket")


class SystemEvent(BaseModel):
    """
    Standardized Q-FLOW System Event Structure.
    Consumable by React frontend and external real-time listeners.
    """

    model_config = ConfigDict(use_enum_values=True)

    event: str = Field(..., description="Event classification (e.g. traffic.updated, incident.created)")
    entity: str = Field(..., description="Target entity or resource (e.g. network, road:R_J1_J2, junction:J1)")
    data: Dict[str, Any] = Field(..., description="Payload data object")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of event generation")


class ConnectionManager:
    """
    WebSocket Connection Manager handling multi-client subscriptions,
    event broadcasts, and safe client disconnects.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accepts and stores incoming WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total active clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Removes disconnected WebSocket safely."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total active clients: {len(self.active_connections)}")

    async def broadcast(self, event: SystemEvent) -> None:
        """Broadcasts SystemEvent JSON string to all connected WebSocket clients asynchronously."""
        if not self.active_connections:
            return

        payload_str = event.model_dump_json()
        disconnected: List[WebSocket] = []

        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload_str)
            except Exception as exc:
                logger.warning(f"Error sending message to WebSocket client: {exc}")
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

    def broadcast_sync(self, event: SystemEvent) -> None:
        """Helper to trigger event broadcast from synchronous methods."""
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                asyncio.create_task(self.broadcast(event))
        except RuntimeError:
            # If no running event loop, ignore or skip
            pass


# Shared manager instance
manager = ConnectionManager()


def broadcast_event(event_type: str, entity: str, data: Dict[str, Any]) -> SystemEvent:
    """Utility function to create and publish a SystemEvent."""
    event = SystemEvent(event=event_type, entity=entity, data=data, timestamp=time.time())
    manager.broadcast_sync(event)
    return event
