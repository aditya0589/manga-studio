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

def clean_panel_dialogue(dialogue_list):
    if not dialogue_list:
        return []
    cleaned = []
    for d in dialogue_list:
        if isinstance(d, dict):
            d_copy = dict(d)
            spk = str(d_copy.get("speaker_name", "Character")).strip()
            if ":" in spk:
                spk = spk.split(":", 1)[0].strip()
            if "(" in spk:
                spk = spk.split("(", 1)[0].strip()
            d_copy["speaker_name"] = spk or "Character"
            cleaned.append(d_copy)
        else:
            cleaned.append(d)
    return cleaned

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
                dialogue=clean_panel_dialogue(p.dialogue),
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
                dialogue=clean_panel_dialogue(p.dialogue),
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

    # Fetch project characters to contextualize new panels
    char_res = await db.execute(select(Character).where(Character.project_id == project.id))
    chars = char_res.scalars().all()
    p_name = next((c.name for c in chars if c.role and c.role.lower() in ("protagonist", "lead")), (chars[0].name if chars else "Hero"))
    r_name = next((c.name for c in chars if c.role and c.role.lower() in ("antagonist", "rival", "supporting") and c.name != p_name), "Rival")

    # Pre-populate 4 distinct progressive panels for this page
    panels_blueprint = [
        {
            "panel_number": 1,
            "script": f"Page {next_page_num} establishing transition: Wide atmospheric shot setting the new dramatic scene.",
            "image_prompt": f"Wide panoramic manga establishing shot, {project.title} setting, dramatic sky and lighting, high contrast ink lineart, screentones",
            "dialogue": [],
            "narration": [{"text": f"The story advances into uncharted territory.", "box_type": "caption", "x": 6.0, "y": 6.0}],
            "sound_effects": [{"text": "WHOOSH", "sfx_type": "ambient", "x": 70.0, "y": 15.0, "size": "medium"}]
        },
        {
            "panel_number": 2,
            "script": f"Medium character action: {p_name} advances with determined expression, analyzing the situation.",
            "image_prompt": f"Medium manga action panel, {p_name} advancing with focused determination, weapon ready, dynamic pose, screentone shading",
            "dialogue": [{"speaker_name": p_name, "text": "We have to stay alert and keep moving.", "bubble_type": "speech", "x": 20.0, "y": 15.0}],
            "narration": [],
            "sound_effects": [{"text": "STEP", "sfx_type": "subtle", "x": 65.0, "y": 65.0, "size": "small"}]
        },
        {
            "panel_number": 3,
            "script": f"Dramatic tension: Low-angle or Dutch tilt shot of unexpected confrontation with {r_name}.",
            "image_prompt": f"Dynamic low-angle tilted manga panel, tense confrontation, shadows deepening, high contrast chiaroscuro inking",
            "dialogue": [{"speaker_name": r_name, "text": "You won't escape so easily!", "bubble_type": "shout", "x": 25.0, "y": 16.0}],
            "narration": [],
            "sound_effects": [{"text": "RUMBLE", "sfx_type": "tension", "x": 55.0, "y": 50.0, "size": "medium"}]
        },
        {
            "panel_number": 4,
            "script": f"Page climax / turning point: High-intensity strike or cliffhanger reaction shot.",
            "image_prompt": f"Epic climactic diagonal manga action panel, explosive power release, dynamic speedlines, dramatic impact debris, masterpiece art",
            "dialogue": [{"speaker_name": p_name, "text": "Then witness my full resolve!", "bubble_type": "shout", "x": 55.0, "y": 15.0}],
            "narration": [],
            "sound_effects": [{"text": "ZKKRAAAK!", "sfx_type": "impact", "x": 10.0, "y": 45.0, "size": "large"}]
        }
    ]

    for p_data in panels_blueprint:
        panel = Panel(
            page_id=new_page.id,
            panel_number=p_data["panel_number"],
            script=p_data["script"],
            image_prompt=p_data["image_prompt"],
            dialogue=p_data["dialogue"],
            narration=p_data["narration"],
            sound_effects=p_data["sound_effects"],
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
            dialogue=clean_panel_dialogue(p.dialogue),
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
    if "dialogue" in data:
        data["dialogue"] = clean_panel_dialogue(data["dialogue"])
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
        dialogue=clean_panel_dialogue(panel.dialogue),
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

    # Retrieve canonical characters and match only relevant characters for THIS panel
    from app.agents.manga_agents import build_character_visual_fingerprint

    char_res = await db.execute(select(Character).where(Character.project_id == project.id))
    all_chars = char_res.scalars().all()

    prompt_to_use = (payload.custom_prompt if payload and payload.custom_prompt else None) or panel.image_prompt or panel.script or "Dynamic manga action scene"

    panel_text = (str(prompt_to_use) + " " + str(panel.script or "")).lower()
    dialogue_speakers = [
        str(d.get("speaker_name", "")).lower()
        for d in (panel.dialogue or [])
        if isinstance(d, dict) and d.get("speaker_name")
    ]

    is_establishing_landscape = (
        (panel.panel_number in (1, 5) or "establishing" in panel_text or "panoramic" in panel_text) and
        any(w in panel_text for w in ["wide", "panoramic", "establishing", "landscape", "sky", "horizon", "ruins", "exterior", "courtyard", "cityscape", "scenery", "ocean", "sea", "mountain"]) and
        not dialogue_speakers and
        not any(c.name.lower() in panel_text for c in all_chars)
    )

    matched_fingerprints = []
    if not is_establishing_landscape:
        for c in all_chars:
            c_name_lower = c.name.lower()
            is_present = (
                c_name_lower in panel_text or
                any(c_name_lower in spk for spk in dialogue_speakers) or
                (not matched_fingerprints and c.role and c.role.lower() in ("protagonist", "lead"))
            )
            if is_present:
                char_dict = {
                    "name": c.name,
                    "role": c.role,
                    "appearance": c.appearance,
                    "canon_data": c.canon_data
                }
                fp = build_character_visual_fingerprint(char_dict)
                if fp and fp not in matched_fingerprints:
                    matched_fingerprints.append(fp)

    char_desc = "; ".join(matched_fingerprints[:2]) if matched_fingerprints else None

    img_provider = get_image_provider()
    result = await img_provider.generate_image(
        prompt=prompt_to_use,
        art_style=project.art_style,
        canonical_descriptions=char_desc,
        genre=project.genre or ""
    )

    if not result.get("success") or not result.get("image_bytes"):
        logger.warning(
            f"Primary image generation failed for panel {panel.panel_number}: {result.get('error')}. "
            "Using Studio Manga Engine fallback."
        )
        from app.providers.mock_provider import MockImageProvider
        result = await MockImageProvider().generate_image(
            prompt=prompt_to_use,
            art_style=project.art_style,
            canonical_descriptions=char_desc,
            genre=project.genre or ""
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
