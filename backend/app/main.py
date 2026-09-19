from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    traffic_router,
    junctions_router,
    roads_router,
    incidents_router,
    scenarios_router,
    emergency_router,
)

app = FastAPI(
    title="Q-FLOW Traffic Network API",
    description="Traffic Network, Simulation Engine, Incident System, and Classical Optimization Baseline API",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(traffic_router)
app.include_router(junctions_router)
app.include_router(roads_router)
app.include_router(incidents_router)
app.include_router(scenarios_router)
app.include_router(emergency_router)



from fastapi import WebSocket, WebSocketDisconnect
from app.websocket.events import manager, SystemEvent
from app.services.traffic_service import traffic_service


@app.websocket("/ws/traffic")
async def websocket_traffic_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint broadcasting real-time Q-FLOW events:
    - traffic.updated
    - signal.updated
    - incident.created
    - incident.updated
    - pedestrian.updated
    """
    await manager.connect(websocket)
    try:
        # Send initial state event snapshot on connection without advancing simulation tick
        active_incs = [inc.incident_id for inc in traffic_service.get_all_incidents(active_only=True)]
        snapshot = TrafficState(
            timestamp=traffic_service.engine.simulation_time,
            roads=traffic_service.network.roads,
            junctions=traffic_service.network.junctions,
            active_incidents=active_incs,
        )
        initial_event = SystemEvent(
            event="traffic.updated",
            entity="network",
            data=snapshot.model_dump(),
        )
        await websocket.send_text(initial_event.model_dump_json())

        # Keep connection open for real-time messages & handle safe client disconnect
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text('{"event":"pong"}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)



@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Q-FLOW Traffic Network Backend API",
        "websocket": "/ws/traffic",
        "version": "0.1.0",
        "documentation": "/docs",
    }



# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred in traffic simulation engine."},
    )
