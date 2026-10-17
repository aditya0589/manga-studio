import os
import mimetypes
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.storage import storage

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("/media/{file_path:path}")
async def serve_media_file(file_path: str):
    """Secure endpoint for serving stored media files."""
    data = await storage.get(file_path)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "image/jpeg" if file_path.endswith((".jpg", ".jpeg")) else "application/octet-stream"

    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=86400"}
    )
