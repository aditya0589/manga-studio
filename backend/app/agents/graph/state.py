from typing import TypedDict, List, Dict, Any, Optional

class MangaWorkflowState(TypedDict):
    # Project & identifiers
    project_id: str
    project_title: Optional[str]
    user_id: str
    chapter_id: Optional[str]
    job_id: str
    art_style: str
    genre: str
    reading_direction: str

    # Uploaded & raw materials
    raw_manuscript: Optional[str]
    uploaded_documents: List[Dict[str, Any]]
    custom_instructions: Optional[str]

    # Ingestion & Story Bible outputs
    premise: str
    synopsis: str
    world_rules: List[str]
    factions_and_locations: List[Dict[str, Any]]
    timeline_events: List[Dict[str, Any]]
    canonical_characters: List[Dict[str, Any]]
    plot_arcs: List[Dict[str, Any]]

    # Cross-chapter continuity context (loaded from DB for chapter N > 1)
    previous_chapter_summaries: List[Dict[str, Any]]

    # Chapter Planning outputs
    chapter_number: int
    chapter_title: str
    chapter_outline: Dict[str, Any]
    outline_approved: bool

    # Scene & Dialogue outputs
    scenes: List[Dict[str, Any]]

    # Director & Panel outputs
    panel_scripts: List[Dict[str, Any]]
    pages: List[Dict[str, Any]]

    # Artwork outputs
    generated_assets: List[Dict[str, Any]]

    # Critic & Continuity
    continuity_issues: List[Dict[str, Any]]
    quality_score: float # 0.0 - 1.0
    revision_count: int
    max_revisions: int

    # Workflow control & logs
    current_stage: str
    status: str # running, approval_required, completed, failed
    error_message: Optional[str]
    progress: int # 0 to 100
