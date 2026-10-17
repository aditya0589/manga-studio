import asyncio
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db, AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.story import StoryDocument, StoryArc
from app.models.character import Character
from app.models.manga import Chapter, Scene, MangaPage, Panel
from app.models.asset import Asset
from app.models.job import GenerationJob
from app.schemas.story import StoryAnalysisRequest, StoryBibleGenerateRequest, StoryBibleResponse
from app.schemas.manga import (
    ChapterCreateRequest,
    ChapterUpdateRequest,
    ChapterResponse,
    ChapterApproveRequest,
    ChapterReviseRequest,
    SceneResponse,
    PageResponse,
    PanelResponse
)
from app.schemas.job import JobResponse
from app.api.dependencies import get_current_user, get_project_with_ownership
from app.workers.job_manager import job_manager
from app.agents.graph.workflow import manga_graph
from app.storage import storage

router = APIRouter(tags=["Story Generation"])

async def run_story_bible_job(job_id: str, project_id: str, user_id: str, instructions: Optional[str]):
    """Background execution for Story Ingestion and Story Bible Generation."""
    await job_manager.broadcast_event(job_id, "job_started", {"stage": "ingest_story", "progress": 10})

    async with AsyncSessionLocal() as session:
        project = await session.get(Project, project_id)
        if not project:
            await job_manager.broadcast_event(job_id, "job_failed", {"error": "Project not found"})
            return

        docs_res = await session.execute(select(StoryDocument).where(StoryDocument.project_id == project_id))
        docs = docs_res.scalars().all()
        doc_data = [{"original_filename": d.original_filename, "extracted_text": d.extracted_text} for d in docs]

        initial_state = {
            "project_id": project_id,
            "user_id": user_id,
            "chapter_id": None,
            "job_id": job_id,
            "art_style": project.art_style,
            "genre": project.genre,
            "reading_direction": project.reading_direction,
            "raw_manuscript": project.synopsis or "",
            "uploaded_documents": doc_data,
            "custom_instructions": instructions,
            "premise": project.synopsis or "",
            "synopsis": "",
            "world_rules": [],
            "factions_and_locations": [],
            "timeline_events": [],
            "canonical_characters": [],
            "plot_arcs": [],
            "chapter_number": 1,
            "chapter_title": "",
            "chapter_outline": {},
            "outline_approved": True,
            "scenes": [],
            "panel_scripts": [],
            "pages": [],
            "generated_assets": [],
            "continuity_issues": [],
            "quality_score": 1.0,
            "revision_count": 0,
            "max_revisions": 2,
            "current_stage": "ingest_story",
            "status": "running",
            "error_message": None,
            "progress": 10
        }

        try:
            # Run agents up to build_story_bible
            from app.agents.story_agents import story_ingestion_node, story_architect_node, character_world_bible_node
            
            await job_manager.broadcast_event(job_id, "stage_started", {"stage": "Story Ingestion", "progress": 20})
            s1 = await story_ingestion_node(initial_state)
            initial_state.update(s1)

            await job_manager.broadcast_event(job_id, "stage_started", {"stage": "Story Architecture", "progress": 40})
            s2 = await story_architect_node(initial_state)
            initial_state.update(s2)

            await job_manager.broadcast_event(job_id, "stage_started", {"stage": "Character & World Bible", "progress": 60})
            s3 = await character_world_bible_node(initial_state)
            initial_state.update(s3)

            # Persist extracted results into DB
            project.synopsis = initial_state.get("synopsis") or initial_state.get("premise")
            
            # Save canonical characters
            for char_info in initial_state.get("canonical_characters", []):
                new_char = Character(
                    project_id=project_id,
                    name=char_info.get("name", "Unnamed Hero"),
                    role=char_info.get("role", "Protagonist"),
                    personality=char_info.get("personality", ""),
                    appearance=char_info.get("appearance", ""),
                    canon_data=char_info.get("canon_data", {}),
                    status="draft"
                )
                session.add(new_char)

            # Save story arcs
            for arc_info in initial_state.get("plot_arcs", []):
                arc = StoryArc(
                    project_id=project_id,
                    title=arc_info.get("title", "Arc"),
                    summary=arc_info.get("summary", ""),
                    order_index=arc_info.get("order_index", 1),
                    outline=arc_info
                )
                session.add(arc)

            project.status = "bible_generated"
            await session.commit()

            await job_manager.broadcast_event(
                job_id,
                "job_completed",
                {
                    "stage": "completed",
                    "progress": 100,
                    "premise": initial_state.get("premise"),
                    "synopsis": initial_state.get("synopsis"),
                    "characters_count": len(initial_state.get("canonical_characters", []))
                }
            )
        except Exception as e:
            await job_manager.broadcast_event(job_id, "job_failed", {"error": str(e)})

@router.post("/projects/{project_id}/analyze", response_model=JobResponse)
async def analyze_project_story(
    project_id: str,
    payload: StoryAnalysisRequest,
    project: Project = Depends(get_project_with_ownership),
    db: AsyncSession = Depends(get_db)
):
    job = GenerationJob(
        project_id=project.id,
        job_type="story_analyze",
        status="queued",
        progress=0,
        current_stage="queued"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Launch background task
    task = asyncio.create_task(run_story_bible_job(job.id, project.id, project.user_id, payload.custom_instructions))
    job_manager.register_task(job.id, task)

    return JobResponse.model_validate(job)

@router.post("/projects/{project_id}/story-bible/generate", response_model=JobResponse)
async def generate_story_bible(
    project_id: str,
    payload: StoryBibleGenerateRequest,
    project: Project = Depends(get_project_with_ownership),
    db: AsyncSession = Depends(get_db)
):
    job = GenerationJob(
        project_id=project.id,
        job_type="story_bible",
        status="queued",
        progress=0,
        current_stage="queued"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    task = asyncio.create_task(run_story_bible_job(job.id, project.id, project.user_id, payload.theme))
    job_manager.register_task(job.id, task)

    return JobResponse.model_validate(job)

async def run_chapter_generation_job(job_id: str, project_id: str, user_id: str, chapter_id: str):
    """Background execution for full chapter generation (planning, scenes, panels, artwork, critic)."""
    await job_manager.broadcast_event(job_id, "job_started", {"stage": "plan_chapter", "progress": 10})

    async with AsyncSessionLocal() as session:
        project = await session.get(Project, project_id)
        chapter = await session.get(Chapter, chapter_id)
        if not project or not chapter:
            await job_manager.broadcast_event(job_id, "job_failed", {"error": "Project or chapter not found"})
            return

        # Fetch canonical characters
        char_res = await session.execute(select(Character).where(Character.project_id == project_id))
        chars = char_res.scalars().all()
        canonical_chars = [{
            "name": c.name,
            "role": c.role,
            "appearance": c.appearance,
            "canon_data": c.canon_data
        } for c in chars]

        # ── Continuity: load story arcs (world rules & plot structure) ──────────
        arc_res = await session.execute(
            select(StoryArc)
            .where(StoryArc.project_id == project_id)
            .order_by(StoryArc.order_index)
        )
        story_arcs = arc_res.scalars().all()
        plot_arcs = [{
            "title": a.title,
            "summary": a.summary,
            "order_index": a.order_index
        } for a in story_arcs]

        # ── Continuity: load summaries of all *previous* completed chapters ────
        prev_chapters_res = await session.execute(
            select(Chapter)
            .where(
                Chapter.project_id == project_id,
                Chapter.order_index < chapter.order_index,
                Chapter.status.in_(["generated", "published", "scripted"])
            )
            .order_by(Chapter.order_index)
        )
        prev_chapters = prev_chapters_res.scalars().all()
        previous_chapter_summaries = [
            {
                "chapter_number": c.order_index,
                "title": c.title,
                "synopsis": c.synopsis or "",
                "key_beats": (c.outline or {}).get("beats", []),
            }
            for c in prev_chapters
        ]

        initial_state = {
            "project_id": project_id,
            "project_title": project.title,
            "user_id": user_id,
            "chapter_id": chapter_id,
            "job_id": job_id,
            "art_style": project.art_style,
            "genre": project.genre,
            "reading_direction": project.reading_direction,
            "raw_manuscript": project.synopsis or "",
            "uploaded_documents": [],
            "custom_instructions": None,
            "premise": project.synopsis or "",
            "synopsis": chapter.synopsis or project.synopsis or "",
            "world_rules": [],
            "factions_and_locations": [],
            "timeline_events": [],
            "canonical_characters": canonical_chars,
            "plot_arcs": plot_arcs,                           # ← loaded from DB
            "previous_chapter_summaries": previous_chapter_summaries,  # ← NEW: continuity
            "chapter_number": chapter.order_index,
            "chapter_title": chapter.title,
            "chapter_outline": chapter.outline or {},
            "outline_approved": True,
            "scenes": [],
            "panel_scripts": [],
            "pages": [],
            "generated_assets": [],
            "continuity_issues": [],
            "quality_score": 1.0,
            "revision_count": 0,
            "max_revisions": 2,
            "current_stage": "plan_chapter",
            "status": "running",
            "error_message": None,
            "progress": 20
        }

        try:
            # Run LangGraph full chapter pipeline
            result_state = await manga_graph.ainvoke(initial_state)

            # Persist chapter outline
            chapter.title = result_state.get("chapter_title", chapter.title)
            chapter.outline = result_state.get("chapter_outline", {})
            chapter.status = "generated"

            # Persist scenes
            for s_info in result_state.get("scenes", []):
                scene = Scene(
                    chapter_id=chapter_id,
                    title=s_info.get("title", "Scene"),
                    summary=s_info.get("summary", ""),
                    script=s_info.get("script", {}),
                    order_index=s_info.get("order_index", 1)
                )
                session.add(scene)
            await session.flush()

            # Persist MangaPage and Panels
            pages_data = result_state.get("pages", [])
            for p_info in pages_data:
                page = MangaPage(
                    chapter_id=chapter_id,
                    page_number=p_info.get("page_number", 1),
                    layout_config=p_info.get("layout_config", {}),
                    status="assembled"
                )
                session.add(page)
                await session.flush()

                for p_script in p_info.get("panels", []):
                    # Check if asset was generated
                    asset_id = None
                    if "asset_info" in p_script:
                        a_info = p_script["asset_info"]
                        asset = Asset(
                            project_id=project_id,
                            asset_type="panel_image",
                            storage_key=a_info["storage_key"],
                            mime_type=a_info.get("mime_type", "image/jpeg"),
                            width=a_info.get("width", 768),
                            height=a_info.get("height", 1024),
                            checksum=a_info.get("checksum"),
                            asset_metadata={"panel_number": p_script.get("panel_number")}
                        )
                        session.add(asset)
                        await session.flush()
                        asset_id = asset.id

                    panel = Panel(
                        page_id=page.id,
                        panel_number=p_script.get("panel_number", 1),
                        script=p_script.get("script"),
                        image_prompt=p_script.get("image_prompt"),
                        dialogue=p_script.get("dialogue", []),
                        narration=p_script.get("narration", []),
                        sound_effects=p_script.get("sound_effects", []),
                        layout_config=p_script.get("layout_config", {}),
                        status="generated" if asset_id else "pending",
                        asset_id=asset_id
                    )
                    session.add(panel)

            await session.commit()

            await job_manager.broadcast_event(
                job_id,
                "job_completed",
                {
                    "stage": "completed",
                    "progress": 100,
                    "chapter_id": chapter_id,
                    "pages_count": len(pages_data),
                    "panels_count": len(result_state.get("panel_scripts", []))
                }
            )
        except Exception as e:
            await job_manager.broadcast_event(job_id, "job_failed", {"error": str(e)})

@router.post("/projects/{project_id}/chapters/generate", response_model=JobResponse)
async def generate_chapter(
    project_id: str,
    payload: ChapterCreateRequest,
    project: Project = Depends(get_project_with_ownership),
    db: AsyncSession = Depends(get_db)
):
    # Create chapter record
    chapter = Chapter(
        project_id=project.id,
        title=payload.title,
        synopsis=payload.synopsis,
        order_index=payload.order_index or 1,
        status="planning",
        outline={}
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)

    job = GenerationJob(
        project_id=project.id,
        chapter_id=chapter.id,
        job_type="chapter_full",
        status="queued",
        progress=0,
        current_stage="queued"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    task = asyncio.create_task(run_chapter_generation_job(job.id, project.id, project.user_id, chapter.id))
    job_manager.register_task(job.id, task)

    return JobResponse.model_validate(job)

@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Chapter)
        .where(Chapter.id == chapter_id)
        .options(
            selectinload(Chapter.scenes),
            selectinload(Chapter.pages).selectinload(MangaPage.panels).selectinload(Panel.asset)
        )
    )
    result = await db.execute(stmt)
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    project = await db.get(Project, chapter.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Serialize pages with image URLs
    pages_res = []
    for pg in chapter.pages:
        panels_res = []
        for p in pg.panels:
            img_url = storage.get_url(p.asset.storage_key) if p.asset else None
            panels_res.append(PanelResponse(
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
        pages_res.append(PageResponse(
            id=pg.id,
            chapter_id=pg.chapter_id,
            page_number=pg.page_number,
            layout_config=pg.layout_config or {},
            status=pg.status,
            created_at=pg.created_at,
            panels=panels_res
        ))

    scenes_res = [SceneResponse.model_validate(s) for s in chapter.scenes]

    return ChapterResponse(
        id=chapter.id,
        project_id=chapter.project_id,
        story_arc_id=chapter.story_arc_id,
        title=chapter.title,
        synopsis=chapter.synopsis,
        outline=chapter.outline or {},
        status=chapter.status,
        order_index=chapter.order_index,
        version=chapter.version,
        created_at=chapter.created_at,
        updated_at=chapter.updated_at,
        scenes=scenes_res,
        pages=pages_res
    )

@router.patch("/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: str,
    payload: ChapterUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    project = await db.get(Project, chapter.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    data = payload.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(chapter, field, val)

    await db.commit()
    await db.refresh(chapter)
    return await get_chapter(chapter_id, current_user, db)

@router.post("/chapters/{chapter_id}/approve")
async def approve_chapter_outline(
    chapter_id: str,
    payload: ChapterApproveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    project = await db.get(Project, chapter.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    chapter.status = "outline_approved"
    outline = chapter.outline or {}
    if payload.approved_beats:
        outline["approved_beats"] = payload.approved_beats
    chapter.outline = outline

    await db.commit()
    return {"message": "Chapter outline approved successfully"}

@router.post("/chapters/{chapter_id}/revise", response_model=JobResponse)
async def revise_chapter(
    chapter_id: str,
    payload: ChapterReviseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    project = await db.get(Project, chapter.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    job = GenerationJob(
        project_id=project.id,
        chapter_id=chapter.id,
        job_type="chapter_revise",
        status="queued",
        progress=0,
        current_stage="queued"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    task = asyncio.create_task(run_chapter_generation_job(job.id, project.id, project.user_id, chapter.id))
    job_manager.register_task(job.id, task)

    return JobResponse.model_validate(job)
