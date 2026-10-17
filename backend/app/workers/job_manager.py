import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, AsyncGenerator
from collections import defaultdict

from app.core.logging import logger
from app.core.database import AsyncSessionLocal
from app.models.job import GenerationJob

class JobManager:
    """Manages asynchronous generation jobs and SSE event broadcasting."""
    def __init__(self):
        # job_id -> list of asyncio.Queue for connected SSE clients
        self.listeners: Dict[str, list[asyncio.Queue]] = defaultdict(list)
        # job_id -> list of historical events for reconnecting clients
        self.event_history: Dict[str, list[dict]] = defaultdict(list)
        # job_id -> running asyncio.Task
        self.active_tasks: Dict[str, asyncio.Task] = {}

    def subscribe(self, job_id: str) -> asyncio.Queue:
        q = asyncio.Queue()
        self.listeners[job_id].append(q)
        return q

    def unsubscribe(self, job_id: str, q: asyncio.Queue):
        if job_id in self.listeners and q in self.listeners[job_id]:
            self.listeners[job_id].remove(q)

    async def broadcast_event(self, job_id: str, event_type: str, data: Dict[str, Any]):
        """Publish an SSE event to all connected clients and store in history."""
        payload = {
            "job_id": job_id,
            "event": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.event_history[job_id].append(payload)

        # Notify active listener queues
        for q in list(self.listeners.get(job_id, [])):
            await q.put(payload)

        # Update persistent job record in DB
        async with AsyncSessionLocal() as session:
            try:
                job = await session.get(GenerationJob, job_id)
                if job:
                    if "progress" in data:
                        job.progress = int(data["progress"])
                    if "stage" in data:
                        job.current_stage = str(data["stage"])
                    if event_type == "job_started":
                        job.status = "running"
                    elif event_type == "job_completed":
                        job.status = "completed"
                        job.progress = 100
                    elif event_type == "job_failed":
                        job.status = "failed"
                        job.error_message = data.get("error", "Unknown error")
                    elif event_type == "approval_required":
                        job.status = "approval_required"

                    job.updated_at = datetime.now(timezone.utc)
                    await session.commit()
            except Exception as e:
                logger.error(f"Failed to update GenerationJob in DB: {e}")

    async def stream_job_events(self, job_id: str) -> AsyncGenerator[str, None]:
        """Yield Server-Sent Events formatted strings for a given job."""
        # First send any missed history
        for past_event in self.event_history.get(job_id, []):
            yield f"event: {past_event['event']}\ndata: {json.dumps(past_event['data'])}\n\n"

        q = self.subscribe(job_id)
        try:
            while True:
                try:
                    event_payload = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield f"event: {event_payload['event']}\ndata: {json.dumps(event_payload['data'])}\n\n"
                    if event_payload["event"] in ("job_completed", "job_failed", "job_cancelled"):
                        break
                except asyncio.TimeoutError:
                    # Send periodic SSE keep-alive ping
                    yield ": ping\n\n"
        finally:
            self.unsubscribe(job_id, q)

    def register_task(self, job_id: str, task: asyncio.Task):
        self.active_tasks[job_id] = task

    def cancel_job(self, job_id: str) -> bool:
        task = self.active_tasks.get(job_id)
        if task and not task.done():
            task.cancel()
            return True
        return False

job_manager = JobManager()
