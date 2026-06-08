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

from typing import Literal

from pydantic import BaseModel


class ItemTags(BaseModel):
    category: Literal["top", "bottom", "shoes"]
    silhouette: str
    palette: list[str]
    texture: str
    aesthetic: str
