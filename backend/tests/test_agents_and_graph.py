import pytest
from app.agents.graph.state import MangaWorkflowState
from app.agents.graph.workflow import manga_graph, quality_gate_router
from app.providers import get_llm_provider, get_image_provider

@pytest.mark.asyncio
async def test_providers_initialization():
    llm = get_llm_provider()
    assert llm is not None
    img = get_image_provider()
    assert img is not None

    res = await llm.generate_text("Test prompt", response_format_json=True)
    assert res["success"] is True
    assert "content" in res

    img_res = await img.generate_image("Test manga panel")
    assert img_res["success"] is True
    assert img_res["image_bytes"] is not None

def test_quality_gate_router():
    # Pass condition
    passing_state = {"quality_score": 0.95, "revision_count": 0, "max_revisions": 2}
    assert quality_gate_router(passing_state) == "layout_pages"

    # Needs revision condition
    failing_state = {"quality_score": 0.65, "revision_count": 0, "max_revisions": 2}
    assert quality_gate_router(failing_state) == "generate_panel_scripts"

    # Revisions exhausted condition
    exhausted_state = {"quality_score": 0.65, "revision_count": 2, "max_revisions": 2}
    assert quality_gate_router(exhausted_state) == "layout_pages"

@pytest.mark.asyncio
async def test_langgraph_full_workflow_execution():
    initial_state = {
        "project_id": "test-proj-123",
        "user_id": "test-user-123",
        "chapter_id": "test-ch-123",
        "job_id": "test-job-123",
        "art_style": "Traditional Manga B&W",
        "genre": "Action and adventure",
        "reading_direction": "right-to-left",
        "raw_manuscript": "Ren, a blacksmith apprentice, discovers a legendary spirit seal blade.",
        "uploaded_documents": [],
        "custom_instructions": None,
        "premise": "",
        "synopsis": "",
        "world_rules": [],
        "factions_and_locations": [],
        "timeline_events": [],
        "canonical_characters": [],
        "plot_arcs": [],
        "chapter_number": 1,
        "chapter_title": "The Awakening",
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
        "current_stage": "initialized",
        "status": "running",
        "error_message": None,
        "progress": 0
    }

    final_state = await manga_graph.ainvoke(initial_state)

    assert final_state["status"] == "completed"
    assert final_state["progress"] == 100
    assert len(final_state["canonical_characters"]) > 0
    assert len(final_state["panel_scripts"]) > 0
    assert len(final_state["pages"]) > 0
    assert len(final_state["generated_assets"]) > 0

@pytest.mark.asyncio
async def test_free_flux_provider_fallback():
    from app.providers.free_flux_provider import FreeFluxImageProvider
    provider = FreeFluxImageProvider()
    res = await provider.generate_image("A samurai confronting his nemesis on a stormy cliff")
    assert res["success"] is True
    assert res["image_bytes"] is not None
    assert len(res["image_bytes"]) > 1000
    assert res["mime_type"] == "image/jpeg"
