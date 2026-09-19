from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from .api import (
    emergencies,
    ambulances,
    hospitals,
    routes,
    optimization,
    emergency,
    traffic,
    junctions,
    roads,
    incidents,
    scenarios,
)
from .services import events
from .services.traffic_service import traffic_service
from .websocket.events import manager, SystemEvent
import time

app = FastAPI(title="Q-FLOW Backend 2 — Emergency & Quantum")


@app.exception_handler(ValueError)
async def value_handler(_, exc: ValueError):
    return JSONResponse(status_code=409, content={"error": str(exc)})


app.include_router(emergencies.router)
app.include_router(ambulances.router)
app.include_router(hospitals.router)
app.include_router(routes.router)
app.include_router(emergency.router)
app.include_router(traffic.router)
app.include_router(junctions.router)
app.include_router(roads.router)
app.include_router(incidents.router)
app.include_router(scenarios.router)
app.include_router(optimization.router)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/")
def root():
    return {"status": "ok", "service": "q-flow"}


@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    q = events.subscribe()
    try:
        while True:
            event = await q.get()
            await ws.send_json(event)
    except WebSocketDisconnect:
        events.unsubscribe(q)


@app.websocket("/ws/traffic")
async def traffic_ws(ws: WebSocket):
    state = traffic_service.get_traffic_state()
    await manager.connect(ws)
    try:
        await ws.send_text(SystemEvent(
            event="traffic.updated",
            entity="network",
            data=state.model_dump(),
            timestamp=time.time(),
        ).model_dump_json())
        while True:
            message = await ws.receive_text()
            if message == "ping":
                await ws.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(ws)
