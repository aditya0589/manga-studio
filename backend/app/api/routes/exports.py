import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.manga import Chapter, MangaPage, Panel
from app.models.publishing import Export
from app.schemas.export import ExportCreateRequest, ExportResponse
from app.api.dependencies import get_current_user, get_project_with_ownership
from app.exporters.pdf_exporter import MangaPDFExporter
from app.storage import storage

router = APIRouter(tags=["Publishing"])

@router.post("/chapters/{chapter_id}/exports", response_model=ExportResponse)
async def export_chapter_pdf(
    chapter_id: str,
    payload: ExportCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Chapter)
        .where(Chapter.id == chapter_id)
        .options(
            selectinload(Chapter.pages).selectinload(MangaPage.panels).selectinload(Panel.asset)
        )
    )
    res = await db.execute(stmt)
    chapter = res.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    project = await db.get(Project, chapter.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Serialize pages with assets
    pages_data = []
    for pg in chapter.pages:
        panels_data = []
        for p in pg.panels:
            asset_info = None
            if p.asset:
                asset_info = {
                    "storage_key": p.asset.storage_key,
                    "mime_type": p.asset.mime_type
                }
            panels_data.append({
                "panel_number": p.panel_number,
                "script": p.script,
                "dialogue": p.dialogue or [],
                "narration": p.narration or [],
                "sound_effects": p.sound_effects or [],
                "asset_info": asset_info
            })
        pages_data.append({
            "page_number": pg.page_number,
            "panels": panels_data
        })

    # Render PDF using MangaPDFExporter
    reading_dir = payload.reading_direction or project.reading_direction
    exporter = MangaPDFExporter(page_size_name=payload.page_size, reading_direction=reading_dir)
    pdf_bytes = exporter.generate_pdf(
        project_title=project.title,
        chapter_title=chapter.title,
        chapter_number=chapter.order_index,
        pages_data=pages_data,
        include_cover=payload.include_cover
    )

    # Save PDF to storage
    export_key = f"projects/{project.id}/exports/{chapter.id}_{uuid.uuid4().hex[:8]}.pdf"
    saved_key = await storage.save(pdf_bytes, export_key, "application/pdf")

    export_record = Export(
        project_id=project.id,
        chapter_id=chapter.id,
        format="pdf",
        storage_key=saved_key,
        status="completed",
        settings=payload.model_dump()
    )
    db.add(export_record)
    await db.commit()
    await db.refresh(export_record)

    download_url = f"/api/v1/exports/{export_record.id}/download"
    return ExportResponse(
        id=export_record.id,
        project_id=export_record.project_id,
        chapter_id=export_record.chapter_id,
        format=export_record.format,
        storage_key=export_record.storage_key,
        status=export_record.status,
        settings=export_record.settings or {},
        download_url=download_url,
        created_at=export_record.created_at
    )

@router.get("/exports/{export_id}", response_model=ExportResponse)
async def get_export(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    exp = await db.get(Export, export_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")

    project = await db.get(Project, exp.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    download_url = f"/api/v1/exports/{exp.id}/download"
    return ExportResponse(
        id=exp.id,
        project_id=exp.project_id,
        chapter_id=exp.chapter_id,
        format=exp.format,
        storage_key=exp.storage_key,
        status=exp.status,
        settings=exp.settings or {},
        download_url=download_url,
        created_at=exp.created_at
    )

@router.get("/exports/{export_id}/download")
async def download_export_file(
    export_id: str,
    db: AsyncSession = Depends(get_db)
):
    exp = await db.get(Export, export_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")

    data = await storage.get(exp.storage_key)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export file missing from storage")

    filename = f"manga_export_{export_id[:8]}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
