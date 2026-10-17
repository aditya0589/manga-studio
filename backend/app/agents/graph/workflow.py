from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

from app.agents.graph.state import MangaWorkflowState
from app.agents.story_agents import (
    story_ingestion_node,
    story_architect_node,
    character_world_bible_node,
    chapter_planner_node
)
from app.agents.manga_agents import (
    scene_dialogue_node,
    manga_director_node,
    art_generation_node,
    critic_continuity_node,
    publishing_node
)
from app.core.logging import logger

def quality_gate_router(state: MangaWorkflowState) -> Literal["generate_panel_scripts", "layout_pages"]:
    """Conditional router: checks if quality review passed or if targeted revision is needed within bounded retries."""
    quality_score = state.get("quality_score", 1.0)
    rev_count = state.get("revision_count", 0)
    max_rev = state.get("max_revisions", 2)

    if quality_score < 0.8 and rev_count < max_rev:
        logger.info(f"Quality gate rejected (score {quality_score:.2f}). Routing to targeted revision (retry {rev_count}/{max_rev}).")
        return "generate_panel_scripts"
    
    logger.info(f"Quality gate approved (score {quality_score:.2f}). Routing to layout pages.")
    return "layout_pages"

def create_manga_workflow():
    """Builds and compiles the end-to-end LangGraph state graph for AI Manga Studio."""
    builder = StateGraph(MangaWorkflowState)

    # Register Nodes
    builder.add_node("ingest_story", story_ingestion_node)
    builder.add_node("architect_story", story_architect_node)
    builder.add_node("build_story_bible", character_world_bible_node)
    builder.add_node("plan_chapter", chapter_planner_node)
    builder.add_node("generate_scenes", scene_dialogue_node)
    builder.add_node("generate_panel_scripts", manga_director_node)
    builder.add_node("generate_artwork", art_generation_node)
    builder.add_node("review_continuity", critic_continuity_node)
    builder.add_node("layout_pages", publishing_node)

    # Sequential edges
    builder.add_edge(START, "ingest_story")
    builder.add_edge("ingest_story", "architect_story")
    builder.add_edge("architect_story", "build_story_bible")
    builder.add_edge("build_story_bible", "plan_chapter")
    builder.add_edge("plan_chapter", "generate_scenes")
    builder.add_edge("generate_scenes", "generate_panel_scripts")
    builder.add_edge("generate_panel_scripts", "generate_artwork")
    builder.add_edge("generate_artwork", "review_continuity")

    # Conditional Quality Gate
    builder.add_conditional_edges(
        "review_continuity",
        quality_gate_router,
        {
            "generate_panel_scripts": "generate_panel_scripts",
            "layout_pages": "layout_pages"
        }
    )

    builder.add_edge("layout_pages", END)

    workflow = builder.compile()
    return workflow

manga_graph = create_manga_workflow()
