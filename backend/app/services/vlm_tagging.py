"""Stage 2 of the ingestion pipeline: send the stripped image to Gemini 2.5 Flash
and validate the structured JSON tags it returns (silhouette, palette, texture, aesthetic).

Calls the Gemini REST API directly via httpx — same lightweight pattern as
backend/scripts/smoke_test.py — rather than pulling in the google-generativeai SDK,
keeping the dependency footprint small for a 4-week MVP. Uses Gemini's structured-output
mode (`responseSchema`) so the model is constrained to the ItemTags shape at generation
time; Pydantic then re-validates at the boundary as a second guard against the PRD's
explicit "broken JSON parsing" quality failure.

Every response MUST be validated with the Pydantic model in app/models/item_tags.py
before it reaches Pinecone or Postgres — see agent_docs/code_patterns.md.
"""

import base64
import os

import httpx
from pydantic import ValidationError

from app.models.item_tags import ItemTags

_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
)

_PROMPT = (
    "You are a fashion cataloguing assistant. Look at this single clothing item "
    "(its background has been removed). Describe it with exactly these five attributes:\n"
    "- category: exactly one of 'top', 'bottom', or 'shoes' "
    "(outerwear/jackets/hoodies/shirts -> 'top'; pants/skirts/shorts -> 'bottom'; "
    "any footwear -> 'shoes')\n"
    "- silhouette: the garment's cut/shape/fit in a few words "
    "(e.g. 'oversized hoodie', 'slim straight-leg jeans')\n"
    "- palette: a list of 1-3 dominant colors in plain English "
    "(e.g. ['heather grey', 'black'])\n"
    "- texture: the fabric/material's visible surface quality "
    "(e.g. 'brushed fleece', 'ribbed knit', 'smooth leather')\n"
    "- aesthetic: the overall style category "
    "(e.g. 'streetwear', 'minimalist', 'preppy', 'athleisure')\n"
    "Respond with only the JSON object — no commentary."
)

_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "category": {"type": "STRING", "enum": ["top", "bottom", "shoes"]},
        "silhouette": {"type": "STRING"},
        "palette": {"type": "ARRAY", "items": {"type": "STRING"}},
        "texture": {"type": "STRING"},
        "aesthetic": {"type": "STRING"},
    },
    "required": ["category", "silhouette", "palette", "texture", "aesthetic"],
}


class TaggingError(Exception):
    """Raised when Gemini's response can't be parsed into valid ItemTags.

    Callers must turn this into a clean user-facing message (e.g. "Couldn't read
    that item, try a clearer photo") rather than letting bad data reach the database —
    see agent_docs/code_patterns.md Error Handling.
    """


def tag_image(image_bytes: bytes, *, mime_type: str = "image/png") -> ItemTags:
    """Send a stripped item photo to Gemini 2.5 Flash and return validated tags."""
    api_key = os.environ["GEMINI_API_KEY"]
    encoded = base64.b64encode(image_bytes).decode("ascii")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": _PROMPT},
                    {"inline_data": {"mime_type": mime_type, "data": encoded}},
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": _RESPONSE_SCHEMA,
        },
    }

    try:
        resp = httpx.post(_GEMINI_URL, params={"key": api_key}, json=payload, timeout=30)
        resp.raise_for_status()
        raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return ItemTags.model_validate_json(raw_text)
    except (httpx.HTTPError, KeyError, IndexError, ValidationError) as e:
        raise TaggingError(f"Gemini returned an unusable response: {e}") from e
