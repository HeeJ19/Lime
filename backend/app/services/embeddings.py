"""Stage 3 of the ingestion pipeline: convert validated item tags into a vector
embedding and upsert it into Pinecone (see agent_docs/tech_stack.md for the index setup).

Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim, runs locally).
Chosen over Gemini's `text-embedding-004` API to keep the dependency family
consistent with RMBG-1.4 (both transformers/torch-based) and to avoid competing
with VLM tagging for Gemini's tight free-tier rate limit. The `lime-items` Pinecone
index was created to match: 384 dimensions, cosine metric, dense vectors, serverless.

Tags are rendered into a natural-language sentence before embedding — semantic
embedding models are trained on prose, not key:value pairs, so a sentence captures
the aesthetic relationships between attributes (e.g. "grey" + "fleece" + "streetwear")
far better than a flat field dump would.
"""

import os

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from app.models.item_tags import ItemTags

_EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None
_index = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_EMBEDDING_MODEL_NAME)
    return _model


def _get_index():
    global _index
    if _index is None:
        pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        _index = pc.Index(os.environ["PINECONE_INDEX_NAME"])
    return _index


def _tags_to_text(tags: ItemTags) -> str:
    palette = " and ".join(tags.palette)
    return (
        f"A {tags.silhouette} in {palette}, with a {tags.texture} texture, "
        f"styled as {tags.aesthetic}."
    )


def embed_and_store(item_id: str, user_id: str, tags: ItemTags) -> None:
    """Embed an item's tags and upsert the resulting vector into Pinecone.

    The vector ID matches the Postgres `items.id` so the two stores stay joined —
    Pinecone is the source of truth for similarity, Postgres for display metadata
    (see agent_docs/code_patterns.md State Management).

    `user_id` and `category` are stored as metadata so the recommendation engine
    can filter a similarity query down to one user's wardrobe within one clothing
    category — without this, a query would search every user's closet at once.
    """
    text = _tags_to_text(tags)
    vector = _get_model().encode(text, normalize_embeddings=True).tolist()

    _get_index().upsert(
        vectors=[
            {
                "id": item_id,
                "values": vector,
                "metadata": {
                    "user_id": user_id,
                    "category": tags.category,
                    "silhouette": tags.silhouette,
                    "palette": tags.palette,
                    "texture": tags.texture,
                    "aesthetic": tags.aesthetic,
                },
            }
        ]
    )
