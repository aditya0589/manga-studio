import json
from typing import Dict, Any, List
from app.agents.graph.state import MangaWorkflowState
from app.providers import get_llm_provider
from app.core.logging import logger
from app.workers.job_manager import job_manager

async def story_ingestion_node(state: MangaWorkflowState) -> Dict[str, Any]:
    """Agent 1: Story Ingestion Agent
    Analyzes uploaded story documents, extracts facts, identifies missing canon."""
    logger.info("Executing Agent 1: Story Ingestion Agent")
    llm = get_llm_provider()

    raw_text = state.get("raw_manuscript", "")
    for doc in state.get("uploaded_documents", []):
        if doc.get("extracted_text"):
            raw_text += f"\n\n--- Document: {doc.get('original_filename')} ---\n" + doc["extracted_text"]

    system_prompt = (
        "You are the Story Ingestion Agent for AI Manga Studio. "
        "Your task is to analyze user-uploaded manuscripts, notes, and world documents. "
        "Extract confirmed facts, summarize the premise, extract distinct characters with personality and appearance, "
        "and isolate world rules. Respond strictly in valid JSON format with keys: "
        "'premise', 'extracted_facts', 'characters', 'world_rules'."
    )
    user_prompt = (
        f"Project Title: {state.get('project_title') or 'Manga Story'}\n"
        f"Genre: {state.get('genre')}\n"
        f"Art Style: {state.get('art_style')}\n"
        f"Existing Characters: {[c.get('name') for c in state.get('canonical_characters', [])]}\n"
        f"Custom Instructions: {state.get('custom_instructions') or 'None'}\n\n"
        f"Uploaded Text Content:\n{raw_text[:6000] if raw_text else (state.get('premise') or ('Create an initial storyline concept for ' + str(state.get('project_title') or 'this manga')))}"
    )

    result = await llm.generate_text(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.6,
        response_format_json=True
    )

    data = result.get("parsed_json") or {}
    premise = data.get("premise") or state.get("premise") or f"A gripping manga tale of {state.get('project_title', 'adventure')}."

    return {
        "premise": premise,
        "current_stage": "ingest_story",
        "progress": 15
    }

async def story_architect_node(state: MangaWorkflowState) -> Dict[str, Any]:
    """Agent 2: Story Architect Agent
    Develops synopsis, conflicts, plot arcs, and stakes."""
    logger.info("Executing Agent 2: Story Architect Agent")
    llm = get_llm_provider()

    system_prompt = (
        "You are the Story Architect Agent for AI Manga Studio. "
        "Your task is to design the overarching narrative arc, stakes, conflicts, and synopsis. "
        "Preserve user-confirmed canon. Respond strictly in valid JSON format with keys: "
        "'synopsis', 'plot_arcs' (list with title, summary, order_index), 'timeline_events'."
    )
    user_prompt = (
        f"Project Title: {state.get('project_title')}\n"
        f"Premise: {state.get('premise')}\n"
        f"Genre: {state.get('genre')}\n"
        f"Characters: {[c.get('name') for c in state.get('canonical_characters', [])]}\n"
        f"Target Audience: Shonen/Seinen Manga\n"
        "Generate a structured narrative arc and high-stakes synopsis."
    )

    result = await llm.generate_text(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.7,
        response_format_json=True
    )

    data = result.get("parsed_json") or {}
    synopsis = data.get("synopsis") or state.get("synopsis") or "An epic conflict erupts as the heroes confront their destined trials."
    plot_arcs = data.get("plot_arcs") or [
        {"title": "The Awakening", "summary": "Initial conflict and awakening of powers.", "order_index": 1},
        {"title": "The Reckoning", "summary": "Climactic showdown against tyrannical forces.", "order_index": 2}
    ]

    return {
        "synopsis": synopsis,
        "plot_arcs": plot_arcs,
        "timeline_events": data.get("timeline_events") or [],
        "current_stage": "architect_story",
        "progress": 30
    }

async def character_world_bible_node(state: MangaWorkflowState) -> Dict[str, Any]:
    """Agent 3: Character and World Bible Agent
    Builds canonical character records with stable traits, visual consistency rules, and world rules."""
    logger.info("Executing Agent 3: Character and World Bible Agent")
    llm = get_llm_provider()

    system_prompt = (
        "You are the Character and World Bible Agent for AI Manga Studio. "
        "Generate canonical character profiles (Protagonist, Antagonist, Allies). "
        "CRITICAL FOR IMAGE CONSISTENCY: Each character MUST have immutable, concrete visual features: "
        "- 'hair': exact cut, style, length, and color (e.g. 'spiky jet-black hair with twin temple bangs') "
        "- 'eyes': exact iris color and eye shape (e.g. 'sharp amber-gold eyes, thin cross scar under left eye') "
        "- 'clothing': exact signature outfit with specific garments and colors (e.g. 'high-collared charcoal sleeveless tunic over white long-sleeve shirt, dark grey pants') "
        "- 'accessories': list of specific signature items (e.g. ['black fingerless combat gloves', 'crimson waist sash']) "
        "- 'visual_consistency_rules': list of 1-2 rules (e.g. ['Always wears crimson waist sash', 'Never removes left glove']) "
        "- 'appearance': a concise 2-sentence summary combining hair, eyes, facial features, and signature outfit. "
        "DO NOT use vague words like 'stylish' or 'cool'. Provide concrete physical descriptions so image diffusion models can draw the character identically in every panel. "
        "Respond strictly in valid JSON format with keys: "
        "'canonical_characters' (list of {name, role, personality, appearance, canon_data: {hair, eyes, clothing, accessories, visual_consistency_rules}}), "
        "'world_rules' (list of strings), 'factions_and_locations' (list)."
    )
    user_prompt = (
        f"Project Title: {state.get('project_title')}\n"
        f"Premise: {state.get('premise')}\n"
        f"Synopsis: {state.get('synopsis')}\n"
        f"Genre: {state.get('genre')}\n"
        f"Existing Characters: {[c.get('name') for c in state.get('canonical_characters', [])]}\n"
        "Generate canonical characters with exact physical and costume visual anchors for image consistency."
    )

    result = await llm.generate_text(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.7,
        response_format_json=True
    )

    data = result.get("parsed_json") or {}
    existing_chars = state.get("canonical_characters") or []
    if existing_chars:
        # Preserve user's custom created characters!
        characters = existing_chars
    else:
        characters = data.get("canonical_characters") or data.get("characters") or []
    world_rules = data.get("world_rules") or state.get("world_rules") or [
        "Special manga aura techniques deplete stamina when overused.",
        "Monochrome high-contrast vision occurs during peak spiritual focus."
    ]

    return {
        "canonical_characters": characters,
        "world_rules": world_rules,
        "factions_and_locations": data.get("factions_and_locations") or [],
        "current_stage": "build_story_bible",
        "progress": 45
    }

async def chapter_planner_node(state: MangaWorkflowState) -> Dict[str, Any]:
    """Agent 4: Chapter Planner Agent
    Plans chapter progression, objectives, story beats, and scene breakdown.
    Reads previous chapter summaries to ensure continuous story flow."""
    logger.info("Executing Agent 4: Chapter Planner Agent")
    job_id = state.get("job_id")
    if job_id:
        await job_manager.broadcast_event(
            job_id,
            "stage_started",
            {
                "stage": "📋 Chapter Planner Agent: Structuring narrative beats and pacing...",
                "progress": 20
            }
        )

    llm = get_llm_provider()

    chapter_num = state.get("chapter_number", 1)
    prev_summaries = state.get("previous_chapter_summaries", [])
    plot_arcs = state.get("plot_arcs", [])

    # Build previous chapter context string for continuity
    prev_context = ""
    if prev_summaries:
        prev_context = "\n\nPREVIOUS CHAPTERS (for continuity — continue the story from here):\n"
        for ch in prev_summaries:
            prev_context += (
                f"Chapter {ch.get('chapter_number')}: {ch.get('title')}\n"
                f"  Synopsis: {ch.get('synopsis', '')[:300]}\n"
                f"  Key beats: {', '.join(ch.get('key_beats', [])[:4])}\n"
            )
    else:
        prev_context = "\n\n(This is Chapter 1 — introduce the world and protagonist.)\n"

    arc_context = ""
    if plot_arcs:
        arc_context = "\nOverarching Plot Arcs:\n" + "\n".join(
            f"  Arc {a.get('order_index', '?')}: {a.get('title')} — {a.get('summary', '')[:200]}"
            for a in plot_arcs
        )

    system_prompt = (
        "You are the Chapter Planner Agent for AI Manga Studio. "
        "Plan the next manga chapter ensuring CONTINUOUS NARRATIVE FLOW from all previous chapters. "
        "Each chapter must advance the overarching plot, develop characters, and escalate stakes. "
        "NEVER repeat events from prior chapters. Reference character growth and unresolved tensions. "
        "Respond strictly in valid JSON format with keys: "
        "'chapter_title', 'synopsis', 'beats' (list of 5–7 dramatic beats as strings), "
        "'scenes_outline' (list of 3–4 {title, summary, order_index})."
    )
    user_prompt = (
        f"Project Title: {state.get('project_title')}\n"
        f"Chapter Number: {chapter_num}\n"
        f"Genre: {state.get('genre', 'Action Fantasy')}\n"
        f"Premise: {state.get('premise')}\n"
        f"Overall Synopsis: {state.get('synopsis')}\n"
        f"Characters: {[c.get('name') for c in state.get('canonical_characters', [])]}\n"
        f"{arc_context}"
        f"{prev_context}\n"
        "Plan a chapter that DIRECTLY CONTINUES the story. Advance character arcs and escalate the central conflict."
    )

    result = await llm.generate_text(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.7,
        response_format_json=True
    )

    data = result.get("parsed_json") or {}
    chapter_title = data.get("chapter_title") or f"Chapter {chapter_num}: The Awakening Call"
    outline = {
        "beats": data.get("beats") or [
            "Introduction to crisis", "Confrontation begins",
            "First reversal", "Climax and revelation", "Resolution and hook"
        ],
        "scenes_outline": data.get("scenes_outline") or [
            {"title": "Scene 1: Shadows Stir", "summary": "Rising tension as enemies approach.", "order_index": 1},
            {"title": "Scene 2: Blade Clash", "summary": "Furious battle and power revelation.", "order_index": 2},
            {"title": "Scene 3: The Aftermath", "summary": "Consequences and next chapter hook.", "order_index": 3}
        ]
    }

    return {
        "chapter_title": chapter_title,
        "chapter_outline": outline,
        "current_stage": "plan_chapter",
        "progress": 60
    }
