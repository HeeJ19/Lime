"""The JSON contract for Gemini's VLM tagging output.

PRD success criteria for Feature 1: Gemini 2.5 Flash must output structured JSON
(silhouette, palette, texture, aesthetic). Broken JSON parsing is an explicit
quality failure — every response is validated against this model before use.

`category` was added beyond the original four PRD attributes: the `items` table
(and the Styling Deck's three swipe stacks) require a top/bottom/shoes
classification, and the PRD's hard requirement is "zero manual entry — just snap
a photo." Having Gemini classify it in the same call (rather than asking the user,
or spending a second Gemini request against its tight free-tier rate limit) is the
only way to satisfy both constraints. It's deliberately excluded from the aesthetic
embedding text in embeddings.py — "is this a top" shouldn't influence style-similarity
matching.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


class ItemTags(BaseModel):
    category: Literal["top", "bottom", "shoes"]
    silhouette: str
    palette: Annotated[list[str], Field(min_length=1)]
    texture: str
    aesthetic: str

    @field_validator("silhouette", "texture", "aesthetic", mode="before")
    @classmethod
    def _strip_and_require(cls, v: object) -> str:
        if not isinstance(v, str):
            raise ValueError("must be a string")
        stripped = v.strip()
        if not stripped:
            raise ValueError("must not be empty")
        return stripped

    @field_validator("palette", mode="before")
    @classmethod
    def _clean_palette(cls, v: object) -> list[str]:
        if not isinstance(v, list):
            raise ValueError("must be a list")
        cleaned = [c.strip() for c in v if isinstance(c, str) and c.strip()]
        if not cleaned:
            raise ValueError("must contain at least one color")
        return cleaned
