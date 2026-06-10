"""Ingestion endpoint: orchestrates the full Vision Ingestion Pipeline
(background removal -> VLM tagging -> embedding -> Pinecone upsert).

This is the FastAPI service's one stateful-feeling output: it mints the
item's UUID so the Pinecone vector ID and the Postgres `items.id` the
frontend later inserts stay joined — without FastAPI ever touching
Postgres itself (it stays a stateless AI microservice; see
docs/ARCHITECTURE.md).

The frontend also passes `user_id` (from the authenticated Supabase session)
as a form field so it can be stored in the Pinecone vector's metadata — the
recommendation engine needs it to scope similarity queries to one user's
wardrobe (see embeddings.embed_and_store).
"""

import base64
import logging
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from app.models.item_tags import ItemTags
from app.services.background_removal import remove_background
from app.services.embeddings import embed_and_store
from app.services.vlm_tagging import TaggingError, tag_image

router = APIRouter(prefix="/items", tags=["items"])

_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB — generous for a phone photo, small enough to fail fast


class IngestResponse(BaseModel):
    item_id: str
    tags: ItemTags
    stripped_image_base64: str


@router.post("/ingest", response_model=IngestResponse)
async def ingest_item(file: UploadFile = File(...), user_id: str = Form(...)) -> IngestResponse:
    if not user_id.strip():
        raise HTTPException(status_code=422, detail="Missing user_id.")

    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=422, detail="Upload must be an image file.")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")
    if len(raw_bytes) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=422, detail="Image is too large (max 10 MB).")

    try:
        stripped_bytes = remove_background(raw_bytes)
    except Exception as e:
        logger.exception("Background removal failed")
        raise HTTPException(
            status_code=502, detail="Couldn't process that photo — try a clearer image."
        ) from e

    try:
        tags = tag_image(stripped_bytes)
    except TaggingError as e:
        logger.exception("VLM tagging failed: %s", e)
        raise HTTPException(
            status_code=502, detail="Couldn't read that item — try a clearer photo."
        ) from e

    item_id = str(uuid.uuid4())

    try:
        embed_and_store(item_id, user_id, tags)
    except Exception as e:
        logger.exception("Embedding/Pinecone store failed")
        raise HTTPException(
            status_code=502, detail="Couldn't index that item — please try again."
        ) from e

    return IngestResponse(
        item_id=item_id,
        tags=tags,
        stripped_image_base64=base64.b64encode(stripped_bytes).decode("ascii"),
    )
