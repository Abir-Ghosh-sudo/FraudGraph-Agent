from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEvent

logger = get_logger("app.streaming")


class EventStreamManager:
    """Manages Server-Sent Events (SSE) subscriber queues for active investigations."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[str | None]]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, investigation_id: str) -> AsyncGenerator[str, None]:
        queue: asyncio.Queue[str | None] = asyncio.Queue()
        async with self._lock:
            self._subscribers[investigation_id].append(queue)
        logger.debug("sse_client_subscribed", investigation_id=investigation_id)

        try:
            # Yield initial connection heartbeat
            yield f"event: ping\ndata: {json.dumps({'time': datetime.now(UTC).isoformat()})}\n\n"

            while True:
                data = await queue.get()
                if data is None:
                    # End of stream sentinel
                    break
                yield data
        except (asyncio.CancelledError, GeneratorExit):
            pass
        finally:
            async with self._lock:
                if queue in self._subscribers[investigation_id]:
                    self._subscribers[investigation_id].remove(queue)
                if not self._subscribers[investigation_id]:
                    self._subscribers.pop(investigation_id, None)
            logger.debug("sse_client_unsubscribed", investigation_id=investigation_id)

    async def publish(self, investigation_id: str, event: AgentEvent | dict[str, Any]) -> None:
        if isinstance(event, AgentEvent):
            event_type = event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type)
            payload_str = event.model_dump_json()
        elif isinstance(event, dict):
            event_type = event.get("event_type", "message")
            payload_str = json.dumps(event, default=str)
        else:
            event_type = "message"
            payload_str = json.dumps({"data": str(event)})

        sse_message = f"event: {event_type}\ndata: {payload_str}\n\n"

        async with self._lock:
            queues = list(self._subscribers.get(investigation_id, []))

        for queue in queues:
            await queue.put(sse_message)

    def publish_sync(self, investigation_id: str, event: AgentEvent | dict[str, Any]) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(investigation_id, event))
        except RuntimeError:
            pass

    async def close_stream(self, investigation_id: str) -> None:
        async with self._lock:
            queues = list(self._subscribers.get(investigation_id, []))
        for queue in queues:
            await queue.put(None)
