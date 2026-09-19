"""In-memory event bus using the shared event format (dict with name + payload)."""
import asyncio

_subscribers: list[asyncio.Queue] = []


def emit(name: str, payload: dict) -> dict:
    event = {"name": name, "payload": payload}
    for q in _subscribers:
        q.put_nowait(event)
    return event


def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.append(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    if q in _subscribers:
        _subscribers.remove(q)
