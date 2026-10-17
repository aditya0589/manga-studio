import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.manga import Chapter, MangaPage, Panel
from app.models.asset import Asset
from app.models.character import Character
from app.schemas.manga import (
    PageResponse,
    PanelResponse,
    PanelUpdateRequest,
    PanelGenerateRequest
)
from app.api.dependencies import get_current_user
from app.providers import get_image_provider
from app.storage import storage, compute_checksum

router = APIRouter(tags=["Manga Editor"])

@router.get("/chapters/{chapter_id}/pages", response_model=List[PageResponse])
async def get_chapter_pages(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    project = await db.get(Project, chapter.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    stmt = (
        select(MangaPage)
        .where(MangaPage.chapter_id == chapter_id)
        .options(selectinload(MangaPage.panels).selectinload(Panel.asset))
        .order_by(MangaPage.page_number)
    )
    res = await db.execute(stmt)
    pages = res.scalars().all()

    output = []
    for pg in pages:
        panels_out = []
        for p in pg.panels:
            img_url = storage.get_url(p.asset.storage_key) if p.asset else None
            panels_out.append(PanelResponse(
                id=p.id,
                page_id=p.page_id,
                scene_id=p.scene_id,
                asset_id=p.asset_id,
                image_url=img_url,
                panel_number=p.panel_number,
                script=p.script,
                image_prompt=p.image_prompt,
                dialogue=p.dialogue or [],
                narration=p.narration or [],
                sound_effects=p.sound_effects or [],
                layout_config=p.layout_config or {},
                status=p.status,
                version=p.version,
                created_at=p.created_at,
                updated_at=p.updated_at
            ))
        output.append(PageResponse(
            id=pg.id,
            chapter_id=pg.chapter_id,
            page_number=pg.page_number,
            layout_config=pg.layout_config or {},
            status=pg.status,
            created_at=pg.created_at,
            panels=panels_out
        ))
    return output

@router.get("/projects/{project_id}/pages", response_model=List[PageResponse])
async def get_project_pages(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await db.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied")

    stmt = (
        select(MangaPage)
        .join(Chapter, MangaPage.chapter_id == Chapter.id)
        .where(Chapter.project_id == project_id)
        .options(selectinload(MangaPage.panels).selectinload(Panel.asset))
        .order_by(MangaPage.page_number)
    )
    res = await db.execute(stmt)
    pages = res.scalars().all()

    output = []
    for pg in pages:
        panels_out = []
        for p in pg.panels:
            img_url = storage.get_url(p.asset.storage_key) if p.asset else None
            panels_out.append(PanelResponse(
                id=p.id,
                page_id=p.page_id,
                scene_id=p.scene_id,
                asset_id=p.asset_id,
                image_url=img_url,
                panel_number=p.panel_number,
                script=p.script,
                image_prompt=p.image_prompt,
                dialogue=p.dialogue or [],
                narration=p.narration or [],
                sound_effects=p.sound_effects or [],
                layout_config=p.layout_config or {},
                status=p.status,
                version=p.version,
                created_at=p.created_at,
                updated_at=p.updated_at
            ))
        output.append(PageResponse(
            id=pg.id,
            chapter_id=pg.chapter_id,
            page_number=pg.page_number,
            layout_config=pg.layout_config or {},
            status=pg.status,
            created_at=pg.created_at,
            panels=panels_out
        ))
    return output

@router.post("/chapters/{chapter_id}/pages", response_model=PageResponse, status_code=status.HTTP_201_CREATED)
async def create_page(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    project = await db.get(Project, chapter.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Get max page number
    stmt = select(MangaPage).where(MangaPage.chapter_id == chapter_id).order_by(MangaPage.page_number.desc())
    res = await db.execute(stmt)
    last_page = res.scalars().first()
    next_page_num = (last_page.page_number + 1) if last_page else 1

    new_page = MangaPage(
        chapter_id=chapter_id,
        page_number=next_page_num,
        layout_config={"grid": "2x2", "reading_direction": project.reading_direction},
        status="assembled"
    )
    db.add(new_page)
    await db.flush()

    # Pre-populate 4 empty panels
    for i in range(1, 5):
        panel = Panel(
            page_id=new_page.id,
            panel_number=i,
            script=f"Panel {i} description",
            image_prompt="High contrast manga panel art, ink lineart, screentones",
            dialogue=[],
            narration=[],
            sound_effects=[],
            layout_config={},
            status="pending"
        )
        db.add(panel)

    await db.commit()
    await db.refresh(new_page)

    # Return refreshed page
    stmt = select(MangaPage).where(MangaPage.id == new_page.id).options(selectinload(MangaPage.panels))
    res = await db.execute(stmt)
    pg = res.scalar_one()

    return PageResponse(
        id=pg.id,
        chapter_id=pg.chapter_id,
        page_number=pg.page_number,
        layout_config=pg.layout_config or {},
        status=pg.status,
        created_at=pg.created_at,
        panels=[PanelResponse(
            id=p.id,
            page_id=p.page_id,
            scene_id=p.scene_id,
            asset_id=p.asset_id,
            image_url=None,
            panel_number=p.panel_number,
            script=p.script,
            image_prompt=p.image_prompt,
            dialogue=p.dialogue or [],
            narration=p.narration or [],
            sound_effects=p.sound_effects or [],
            layout_config=p.layout_config or {},
            status=p.status,
            version=p.version,
            created_at=p.created_at,
            updated_at=p.updated_at
        ) for p in pg.panels]
    )

@router.patch("/panels/{panel_id}", response_model=PanelResponse)
async def update_panel(
    panel_id: str,
    payload: PanelUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Panel).where(Panel.id == panel_id).options(selectinload(Panel.asset))
    res = await db.execute(stmt)
    panel = res.scalar_one_or_none()
    if not panel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Panel not found")

    page = await db.get(MangaPage, panel.page_id)
    chapter = await db.get(Chapter, page.chapter_id)
    project = await db.get(Project, chapter.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    data = payload.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(panel, field, val)

    panel.version += 1
    await db.commit()
    await db.refresh(panel)

    img_url = storage.get_url(panel.asset.storage_key) if panel.asset else None
    return PanelResponse(
        id=panel.id,
        page_id=panel.page_id,
        scene_id=panel.scene_id,
        asset_id=panel.asset_id,
        image_url=img_url,
        panel_number=panel.panel_number,
        script=panel.script,
        image_prompt=panel.image_prompt,
        dialogue=panel.dialogue or [],
        narration=panel.narration or [],
        sound_effects=panel.sound_effects or [],
        layout_config=panel.layout_config or {},
        status=panel.status,
        version=panel.version,
        created_at=panel.created_at,
        updated_at=panel.updated_at
    )

@router.post("/panels/{panel_id}/generate", response_model=PanelResponse)
@router.post("/panels/{panel_id}/regenerate", response_model=PanelResponse)
async def generate_panel_artwork(
    panel_id: str,
    payload: Optional[PanelGenerateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Panel).where(Panel.id == panel_id).options(selectinload(Panel.asset))
    res = await db.execute(stmt)
    panel = res.scalar_one_or_none()
    if not panel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Panel not found")

    page = await db.get(MangaPage, panel.page_id)
    chapter = await db.get(Chapter, page.chapter_id)
    project = await db.get(Project, chapter.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    panel.status = "generating"
    await db.commit()

    # Retrieve canonical character descriptions for consistency
    char_desc = ""
    char_res = await db.execute(select(Character).where(Character.project_id == project.id))
    for c in char_res.scalars().all():
        char_desc += f"{c.name}: {c.appearance}. "

    prompt_to_use = (payload.custom_prompt if payload and payload.custom_prompt else None) or panel.image_prompt or panel.script or "Dynamic manga action scene"

    img_provider = get_image_provider()
    result = await img_provider.generate_image(
        prompt=prompt_to_use,
        art_style=project.art_style,
        canonical_descriptions=char_desc
    )

    if not result.get("success") or not result.get("image_bytes"):
        panel.status = "error"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {result.get('error')}"
        )

    # Save to storage
    storage_key = f"projects/{project.id}/panels/panel_{panel.panel_number}_{uuid.uuid4().hex[:8]}.jpg"
    saved_key = await storage.save(result["image_bytes"], storage_key, result["mime_type"])
    checksum = compute_checksum(result["image_bytes"])

    asset = Asset(
        project_id=project.id,
        asset_type="panel_image",
        storage_key=saved_key,
        mime_type=result.get("mime_type", "image/jpeg"),
        width=result.get("width", 768),
        height=result.get("height", 1024),
        file_size=len(result["image_bytes"]),
        checksum=checksum,
        asset_metadata={"panel_id": panel.id, "prompt": prompt_to_use}
    )
    db.add(asset)
    await db.flush()

    panel.asset_id = asset.id
    panel.status = "generated"
    panel.version += 1
    await db.commit()
    await db.refresh(panel)

    return PanelResponse(
        id=panel.id,
        page_id=panel.page_id,
        scene_id=panel.scene_id,
        asset_id=panel.asset_id,
        image_url=storage.get_url(saved_key),
        panel_number=panel.panel_number,
        script=panel.script,
        image_prompt=panel.image_prompt,
        dialogue=panel.dialogue or [],
        narration=panel.narration or [],
        sound_effects=panel.sound_effects or [],
        layout_config=panel.layout_config or {},
        status=panel.status,
        version=panel.version,
        created_at=panel.created_at,
        updated_at=panel.updated_at
    )

@router.post("/panels/{panel_id}/approve", response_model=PanelResponse)
async def approve_panel(
    panel_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Panel).where(Panel.id == panel_id).options(selectinload(Panel.asset))
    res = await db.execute(stmt)
    panel = res.scalar_one_or_none()
    if not panel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Panel not found")

    panel.status = "approved"
    await db.commit()
    await db.refresh(panel)

    img_url = storage.get_url(panel.asset.storage_key) if panel.asset else None
    return PanelResponse(
        id=panel.id,
        page_id=panel.page_id,
        scene_id=panel.scene_id,
        asset_id=panel.asset_id,
        image_url=img_url,
        panel_number=panel.panel_number,
        script=panel.script,
        image_prompt=panel.image_prompt,
        dialogue=panel.dialogue or [],
        narration=panel.narration or [],
        sound_effects=panel.sound_effects or [],
        layout_config=panel.layout_config or {},
        status=panel.status,
        version=panel.version,
        created_at=panel.created_at,
        updated_at=panel.updated_at
    )
