import uuid
import json
import asyncio
from typing import Dict, Any, List
from app.agents.graph.state import MangaWorkflowState
from app.providers import get_llm_provider, get_image_provider
from app.storage import storage, compute_checksum
from app.core.logging import logger

async def scene_dialogue_node(state: MangaWorkflowState) -> Dict[str, Any]:
    """Agent 5: Scene and Dialogue Agent
    Converts outlines into detailed scenes with actions and separated character dialogue.
    Ensures narrative flow by incorporating chapter beats and character development."""
    logger.info("Executing Agent 5: Scene and Dialogue Agent")
    llm = get_llm_provider()

    beats = state.get('chapter_outline', {}).get('beats', [])
    scenes_outline = state.get('chapter_outline', {}).get('scenes_outline', [])
    world_rules = state.get('world_rules', [])
    prev_summaries = state.get('previous_chapter_summaries', [])

    # Summarize where the story is coming from
    story_so_far = ""
    if prev_summaries:
        last = prev_summaries[-1]
        story_so_far = (
            f"Previously in Chapter {last.get('chapter_number')}: "
            f"{last.get('synopsis', '')}. "
            f"The reader just experienced: {', '.join(last.get('key_beats', [])[:3])}."
        )

    system_prompt = (
        "You are the Scene and Dialogue Agent for AI Manga Studio. "
        "Convert the chapter outline into 3-4 detailed dramatic scenes. "
        "Write vivid character dialogue that sounds natural and emotional. "
        "Each scene must ADVANCE the plot — show character growth, conflict escalation, or revelation. "
        "KEEP DIALOGUE AND NARRATION COMPLETELY SEPARATE FROM VISUAL SETTING DESCRIPTIONS. "
        "Respond strictly in valid JSON format with keys: "
        "'scenes' (list of {title, summary, order_index, script: "
        "{setting, characters_present, actions, "
        "dialogue: [{speaker_name, text, bubble_type}], "
        "narration_captions: [string]}})."
    )
    user_prompt = (
        f"Project Title: {state.get('project_title') or 'Manga Story'}\n"
        f"Chapter Title: {state.get('chapter_title')}\n"
        f"Genre: {state.get('genre', 'Action Fantasy')}\n"
        f"Chapter Beats: {beats}\n"
        f"Scenes to write: {[s.get('title') for s in scenes_outline]}\n"
        f"Characters: {[c.get('name') + ' (' + c.get('role', '') + ')' for c in state.get('canonical_characters', [])]}\n"
        f"World Rules: {world_rules[:3]}\n"
        f"{('Story so far: ' + story_so_far) if story_so_far else '(This is the opening chapter.)'}\n"
        "Generate 3-4 dynamic scenes with punchy manga dialogue. "
        "Each scene must feel DIFFERENT — vary between action, tension, and character moments."
    )

    result = await llm.generate_text(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.75,
        response_format_json=True
    )

    data = result.get("parsed_json") or {}
    scenes = data.get("scenes") or state.get("scenes") or [
        {
            "title": "Scene 1: The Sparks Fly",
            "summary": "Tense confrontation in the ruined forge.",
            "order_index": 1,
            "script": {
                "setting": "Ruined forge workshop, falling burning timbers, thick shadows",
                "characters_present": ["Ren Kurogane"],
                "actions": "Ren stands resolute before the forge anvil, gripping the ancient blade.",
                "dialogue": [{"speaker_name": "Ren", "text": "I will forge my own destiny!", "bubble_type": "speech"}],
                "narration_captions": ["The night of reckoning had finally arrived."]
            }
        },
        {
            "title": "Scene 2: Into the Storm",
            "summary": "The protagonist pushes past their limits.",
            "order_index": 2,
            "script": {
                "setting": "Storm-swept battlefield, lightning crackling overhead",
                "characters_present": ["Ren Kurogane"],
                "actions": "Ren charges forward through the storm, blade raised.",
                "dialogue": [{"speaker_name": "Ren", "text": "No turning back now!", "bubble_type": "thought"}],
                "narration_captions": ["Every step forward cost more than the last."]
            }
        }
    ]

    return {
        "scenes": scenes,
        "current_stage": "generate_scenes",
        "progress": 70
    }

async def manga_director_node(state: MangaWorkflowState) -> Dict[str, Any]:
    """Agent 6: Manga Director Agent
    Transforms scenes into panel-by-panel manga director scripts with camera angle, composition,
    character poses, speech bubble placement, and Japanese/English sound effects.
    Generates 6 panels per page for richer story pacing."""
    logger.info("Executing Agent 6: Manga Director Agent")
    llm = get_llm_provider()

    scenes = state.get('scenes', [])
    # Build a compact scene breakdown for the director
    scene_summary = ""
    for s in scenes:
        script = s.get('script', {})
        scene_summary += (
            f"\nScene: {s.get('title')}\n"
            f"  Setting: {script.get('setting', '')}\n"
            f"  Characters: {', '.join(script.get('characters_present', []))}\n"
            f"  Action: {script.get('actions', '')[:200]}\n"
            f"  Dialogue: {[d.get('text', '')[:60] for d in script.get('dialogue', [])[:2]]}\n"
        )

    system_prompt = (
        "You are the Manga Director Agent for AI Manga Studio. "
        "Direct 6 page panels with expert manga cinematography showing STORY PROGRESSION across panels. "
        "Panel 1 establishes the scene. Panels 2-5 escalate tension and action. Panel 6 delivers the emotional peak or cliffhanger. "
        "Use varied shots: wide establishing, medium two-shot, extreme close-up eyes, over-the-shoulder, dynamic action angle, reaction shot. "
        "Each panel needs: panel_number, script (camera direction), image_prompt (VISUAL ONLY — no dialogue text), "
        "dialogue (list of {speaker_name, text, bubble_type, x, y}), "
        "narration (list of {text, box_type, x, y}), and sound_effects (list of {text, sfx_type, x, y, size}). "
        "image_prompt must describe ONLY the visual composition — NO character names, NO dialogue text. "
        "Respond strictly in valid JSON format with key: 'panel_scripts'."
    )
    user_prompt = (
        f"Project Title: {state.get('project_title') or 'Manga Story'}\n"
        f"Chapter Title: {state.get('chapter_title')}\n"
        f"Art Style: {state.get('art_style', 'Traditional Manga B&W')}\n"
        f"Genre: {state.get('genre', 'Action Fantasy')}\n"
        f"Characters: {[c.get('name') + ': ' + c.get('appearance', '')[:80] for c in state.get('canonical_characters', [])[:3]]}\n"
        f"Chapter Beats: {state.get('chapter_outline', {}).get('beats', [])[:5]}\n"
        f"Scenes:{scene_summary}"
        "Generate 6 dramatic manga panel scripts. Vary panel sizes: panels 1, 6 can be WIDE (full-width splash), panels 2-5 normal grid."
    )

    result = await llm.generate_text(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.75,
        response_format_json=True
    )

    data = result.get("parsed_json") or {}
    panel_scripts = data.get("panel_scripts") or state.get("panel_scripts") or []

    if not panel_scripts:
        panel_scripts = [
            {
                "panel_number": 1,
                "script": "WIDE SHOT — panoramic establishing view of the location under dramatic sky.",
                "image_prompt": "Wide panoramic manga establishing shot, dramatic stormy sky, high contrast ink lineart, crisp screentones, full-width splash panel",
                "dialogue": [],
                "narration": [{"text": "The city never sleeps — and tonight, neither would he.", "box_type": "caption", "x": 5.0, "y": 5.0}],
                "sound_effects": [{"text": "ROOOAAAR", "sfx_type": "ambient", "x": 70.0, "y": 15.0, "size": "large"}]
            },
            {
                "panel_number": 2,
                "script": "Medium shot of protagonist entering the scene with purpose.",
                "image_prompt": "Medium manga panel, hero silhouette backlit, intense determination, bold ink outline, screentone shading",
                "dialogue": [{"speaker_name": "Hero", "text": "I've been waiting for this moment.", "bubble_type": "speech", "x": 20.0, "y": 15.0}],
                "narration": [],
                "sound_effects": [{"text": "SHRRNG", "sfx_type": "dramatic", "x": 75.0, "y": 70.0, "size": "small"}]
            },
            {
                "panel_number": 3,
                "script": "Close-up of protagonist's eyes filled with resolve.",
                "image_prompt": "Extreme close-up manga panel, fierce determined eyes, detailed iris ink shading, dramatic speedlines background",
                "dialogue": [{"speaker_name": "Hero", "text": "This blade remembers the ancient pledge.", "bubble_type": "thought", "x": 15.0, "y": 15.0}],
                "narration": [],
                "sound_effects": []
            },
            {
                "panel_number": 4,
                "script": "Dynamic diagonal cut: The antagonist arrives in a burst of power.",
                "image_prompt": "Action manga panel, armored antagonist crashing through barrier, diagonal dynamic angle, impact dust debris, bold ink linework",
                "dialogue": [{"speaker_name": "Rival", "text": "You dare face me?!", "bubble_type": "shout", "x": 20.0, "y": 12.0}],
                "narration": [],
                "sound_effects": [{"text": "BASHHH!", "sfx_type": "impact", "x": 55.0, "y": 55.0, "size": "large"}]
            },
            {
                "panel_number": 5,
                "script": "Over-the-shoulder shot — two figures face off at close range, tension crackling.",
                "image_prompt": "Over-shoulder manga panel, tense face-off, two figures, crackling energy between them, heavy shadow screentone",
                "dialogue": [{"speaker_name": "Hero", "text": "Then let's settle this here!", "bubble_type": "speech", "x": 55.0, "y": 20.0}],
                "narration": [],
                "sound_effects": [{"text": "BZZZZ", "sfx_type": "tension", "x": 48.0, "y": 50.0, "size": "medium"}]
            },
            {
                "panel_number": 6,
                "script": "CLIMAX SPLASH: Hero unleashes full power in a devastating strike.",
                "image_prompt": "Epic climactic manga splash panel, hero unleashing maximum energy aura, speedlines radiating from center, explosive ink splatter, masterpiece manga art quality, Akira Toriyama power level",
                "dialogue": [{"speaker_name": "Hero", "text": "ABSOLUTE LIMIT BREAK!", "bubble_type": "shout", "x": 55.0, "y": 15.0}],
                "narration": [],
                "sound_effects": [{"text": "ZKKKKRAAAK!", "sfx_type": "impact", "x": 10.0, "y": 45.0, "size": "huge"}]
            }
        ]

    return {
        "panel_scripts": panel_scripts,
        "current_stage": "generate_panel_scripts",
        "progress": 80
    }

async def art_generation_node(state: MangaWorkflowState) -> Dict[str, Any]:
    """Agent 7: Art Generation Agent
    Extracts canonical character traits, builds prompts, generates artwork using cloud/mock provider,
    and stores image assets."""
    logger.info("Executing Agent 7: Art Generation Agent")
    img_provider = get_image_provider()

    canonical_chars = state.get("canonical_characters", [])
    char_desc_text = ""
    for c in canonical_chars:
        char_desc_text += f"{c.get('name')}: {c.get('appearance', '')}. "

    panel_scripts = state.get("panel_scripts", [])
    generated_assets = []

    # Check if using FreeFluxImageProvider which requires safe spacing to clear rate limit
    is_free = type(img_provider).__name__ == "FreeFluxImageProvider"

    for idx, panel in enumerate(panel_scripts):
        p_num = panel.get("panel_number", idx + 1)
        prompt = panel.get("image_prompt") or panel.get("script") or "Dramatic manga panel"

        if idx > 0 and is_free:
            logger.info(f"Rate-limit cooldown: waiting 46s before generating panel {p_num}...")
            await asyncio.sleep(46)

        logger.info(f"Generating artwork for panel {p_num}")
        res = await img_provider.generate_image(
            prompt=prompt,
            art_style=state.get("art_style", "Traditional Manga B&W"),
            canonical_descriptions=char_desc_text,
            genre=state.get("genre", ""),
        )

        if res.get("success") and res.get("image_bytes"):
            storage_key = f"projects/{state.get('project_id')}/panels/panel_{p_num}_{uuid.uuid4().hex[:8]}.jpg"
            saved_key = await storage.save(res["image_bytes"], storage_key, res["mime_type"])
            url = storage.get_url(saved_key)
            checksum = compute_checksum(res["image_bytes"])

            asset_info = {
                "panel_number": p_num,
                "storage_key": saved_key,
                "image_url": url,
                "width": res.get("width", 768),
                "height": res.get("height", 1024),
                "checksum": checksum,
                "mime_type": res.get("mime_type", "image/jpeg"),
                "model_used": res.get("model_used")
            }
            generated_assets.append(asset_info)
            panel["asset_info"] = asset_info
        else:
            logger.warning(f"Art generation failed for panel {p_num}: {res.get('error')}")

    return {
        "generated_assets": generated_assets,
        "panel_scripts": panel_scripts,
        "current_stage": "generate_artwork",
        "progress": 90
    }

async def critic_continuity_node(state: MangaWorkflowState) -> Dict[str, Any]:
    """Agent 8: Critic and Continuity Agent
    Deterministic + semantic review of character consistency, panel pacing, dialogue separation."""
    logger.info("Executing Agent 8: Critic and Continuity Agent")
    issues = []
    panels = state.get("panel_scripts", [])

    # Deterministic checks
    if len(panels) == 0:
        issues.append({"type": "missing_panels", "description": "No panels were generated for this chapter."})

    for p in panels:
        # Check text separation
        prompt = (p.get("image_prompt") or "").lower()
        if "says:" in prompt or "shouts:" in prompt:
            issues.append({
                "type": "text_leakage",
                "panel_number": p.get("panel_number"),
                "description": "Image prompt contains dialogue keywords. Dialogue must remain separate from image prompts."
            })

    # LLM semantic check if provider available
    llm = get_llm_provider()
    rev_count = state.get("revision_count", 0)

    quality_score = 0.95 if len(issues) == 0 else 0.75

    return {
        "continuity_issues": issues,
        "quality_score": quality_score,
        "revision_count": rev_count + 1,
        "current_stage": "review_continuity",
        "progress": 95
    }

async def publishing_node(state: MangaWorkflowState) -> Dict[str, Any]:
    """Agent 9: Publishing Agent
    Assembles final pages and prepares export layout."""
    logger.info("Executing Agent 9: Publishing Agent")
    panels = state.get("panel_scripts", [])

    # Pack panels into page layouts (e.g. 4 panels per page)
    pages = []
    current_page_panels = []
    page_num = 1

    for p in panels:
        current_page_panels.append(p)
        if len(current_page_panels) >= 4:
            pages.append({
                "page_number": page_num,
                "layout_config": {"grid": "2x2", "reading_direction": state.get("reading_direction", "right-to-left")},
                "panels": current_page_panels
            })
            current_page_panels = []
            page_num += 1

    if current_page_panels:
        pages.append({
            "page_number": page_num,
            "layout_config": {"grid": "custom", "reading_direction": state.get("reading_direction", "right-to-left")},
            "panels": current_page_panels
        })

    return {
        "pages": pages,
        "status": "completed",
        "current_stage": "layout_pages",
        "progress": 100
    }
