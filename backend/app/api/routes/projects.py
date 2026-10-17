from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse
from app.api.dependencies import get_current_user, get_project_with_ownership

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    search: Optional[str] = None,
    genre: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Project).where(Project.user_id == current_user.id)
    if search:
        stmt = stmt.where(Project.title.ilike(f"%{search}%"))
    if genre:
        stmt = stmt.where(Project.genre == genre)
    if status_filter:
        stmt = stmt.where(Project.status == status_filter)

    stmt = stmt.order_by(desc(Project.updated_at))
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return [ProjectResponse.model_validate(p) for p in projects]

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_project = Project(
        user_id=current_user.id,
        title=payload.title,
        synopsis=payload.synopsis,
        genre=payload.genre,
        language=payload.language,
        art_style=payload.art_style,
        reading_direction=payload.reading_direction,
        target_audience=payload.target_audience,
        status="planning",
        settings=payload.settings or {}
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return ProjectResponse.model_validate(new_project)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project: Project = Depends(get_project_with_ownership)
):
    return ProjectResponse.model_validate(project)

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    payload: ProjectUpdateRequest,
    project: Project = Depends(get_project_with_ownership),
    db: AsyncSession = Depends(get_db)
):
    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(project, field, val)

    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project: Project = Depends(get_project_with_ownership),
    db: AsyncSession = Depends(get_db)
):
    await db.delete(project)
    await db.commit()
    return None
