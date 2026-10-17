import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.character import Character, CharacterReference
from app.models.asset import Asset
from app.schemas.character import (
    CharacterCreateRequest,
    CharacterUpdateRequest,
    CharacterResponse,
    ReferenceResponse,
    ApproveDesignRequest
)
from app.api.dependencies import get_current_user, get_project_with_ownership
from app.storage import storage, compute_checksum

router = APIRouter(tags=["Characters"])

@router.get("/projects/{project_id}/characters", response_model=List[CharacterResponse])
async def list_characters(
    project: Project = Depends(get_project_with_ownership),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Character)
        .where(Character.project_id == project.id)
        .options(selectinload(Character.references).selectinload(CharacterReference.asset))
        .order_by(Character.created_at)
    )
    result = await db.execute(stmt)
    chars = result.scalars().all()

    output = []
    for c in chars:
        refs = []
        for r in c.references:
            img_url = storage.get_url(r.asset.storage_key) if r.asset else None
            refs.append(ReferenceResponse(
                id=r.id,
                character_id=r.character_id,
                asset_id=r.asset_id,
                reference_type=r.reference_type,
                approval_status=r.approval_status,
                image_url=img_url
            ))
        char_dict = CharacterResponse(
            id=c.id,
            project_id=c.project_id,
            name=c.name,
            role=c.role,
            personality=c.personality,
            appearance=c.appearance,
            canon_data=c.canon_data or {},
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at,
            references=refs
        )
        output.append(char_dict)
    return output

@router.post("/projects/{project_id}/characters", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    payload: CharacterCreateRequest,
    project: Project = Depends(get_project_with_ownership),
    db: AsyncSession = Depends(get_db)
):
    new_char = Character(
        project_id=project.id,
        name=payload.name,
        role=payload.role,
        personality=payload.personality,
        appearance=payload.appearance,
        canon_data=payload.canon_data or {},
        status="draft"
    )
    db.add(new_char)
    await db.commit()
    await db.refresh(new_char)

    return CharacterResponse(
        id=new_char.id,
        project_id=new_char.project_id,
        name=new_char.name,
        role=new_char.role,
        personality=new_char.personality,
        appearance=new_char.appearance,
        canon_data=new_char.canon_data or {},
        status=new_char.status,
        created_at=new_char.created_at,
        updated_at=new_char.updated_at,
        references=[]
    )

@router.patch("/characters/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str,
    payload: CharacterUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    char = await db.get(Character, character_id)
    if not char:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    project = await db.get(Project, char.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    data = payload.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(char, field, val)

    await db.commit()
    await db.refresh(char)

    return CharacterResponse(
        id=char.id,
        project_id=char.project_id,
        name=char.name,
        role=char.role,
        personality=char.personality,
        appearance=char.appearance,
        canon_data=char.canon_data or {},
        status=char.status,
        created_at=char.created_at,
        updated_at=char.updated_at,
        references=[]
    )

@router.post("/characters/{character_id}/references", response_model=ReferenceResponse)
async def upload_character_reference(
    character_id: str,
    file: UploadFile = File(...),
    reference_type: str = Form("canonical_face"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    char = await db.get(Character, character_id)
    if not char:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    project = await db.get(Project, char.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    content = await file.read()
    ext = os.path.splitext(file.filename or ".png")[1]
    storage_key = f"projects/{project.id}/characters/{char.id}_{uuid.uuid4().hex[:8]}{ext}"
    saved_key = await storage.save(content, storage_key, file.content_type or "image/png")
    checksum = compute_checksum(content)

    asset = Asset(
        project_id=project.id,
        asset_type="character_ref",
        storage_key=saved_key,
        mime_type=file.content_type or "image/png",
        file_size=len(content),
        checksum=checksum,
        asset_metadata={"original_filename": file.filename, "character_name": char.name}
    )
    db.add(asset)
    await db.flush()

    ref = CharacterReference(
        character_id=char.id,
        asset_id=asset.id,
        reference_type=reference_type,
        approval_status="pending"
    )
    db.add(ref)
    await db.commit()
    await db.refresh(ref)

    return ReferenceResponse(
        id=ref.id,
        character_id=ref.character_id,
        asset_id=ref.asset_id,
        reference_type=ref.reference_type,
        approval_status=ref.approval_status,
        image_url=storage.get_url(saved_key)
    )

@router.post("/characters/{character_id}/approve-design")
async def approve_character_design(
    character_id: str,
    payload: ApproveDesignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    char = await db.get(Character, character_id)
    if not char:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    project = await db.get(Project, char.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    char.status = "approved"
    if payload.canonical_appearance:
        char.appearance = payload.canonical_appearance

    canon = char.canon_data or {}
    if payload.visual_consistency_rules:
        canon["visual_consistency_rules"] = payload.visual_consistency_rules
    char.canon_data = canon

    if payload.reference_id:
        ref = await db.get(CharacterReference, payload.reference_id)
        if ref and ref.character_id == char.id:
            ref.approval_status = "approved"

    await db.commit()
    return {"message": "Character design approved and locked into canon"}
