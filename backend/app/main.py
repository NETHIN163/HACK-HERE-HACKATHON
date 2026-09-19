from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from .api import emergencies, ambulances, hospitals, routes, optimization, emergency
from .services import events

app = FastAPI(title="Q-FLOW Backend 2 — Emergency & Quantum")


@app.exception_handler(ValueError)
async def value_handler(_, exc: ValueError):
    return JSONResponse(status_code=409, content={"error": str(exc)})


app.include_router(emergencies.router)
app.include_router(ambulances.router)
app.include_router(hospitals.router)
app.include_router(routes.router)
app.include_router(optimization.router)
app.include_router(emergency.router)


@app.get("/health")
def health():
    return {"ok": True}


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
