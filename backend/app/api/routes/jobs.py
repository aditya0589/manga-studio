from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.job import GenerationJob
from app.models.project import Project
from app.schemas.job import JobResponse
from app.api.dependencies import get_current_user
from app.workers.job_manager import job_manager

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job = await db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    project = await db.get(Project, job.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return JobResponse.model_validate(job)

@router.get("/{job_id}/events")
async def stream_job_events(job_id: str):
    """Server-Sent Events endpoint streaming real-time generation progress."""
    return StreamingResponse(
        job_manager.stream_job_events(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job = await db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    project = await db.get(Project, job.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    cancelled = job_manager.cancel_job(job_id)
    if cancelled:
        job.status = "cancelled"
        await db.commit()
        await job_manager.broadcast_event(job_id, "job_cancelled", {"message": "Job cancelled by user"})
        return {"message": "Job successfully cancelled"}
    else:
        return {"message": "Job could not be cancelled or was already finished"}

@router.post("/{job_id}/resume", response_model=JobResponse)
async def resume_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job = await db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    project = await db.get(Project, job.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    job.status = "running"
    await db.commit()
    await db.refresh(job)
    return JobResponse.model_validate(job)
