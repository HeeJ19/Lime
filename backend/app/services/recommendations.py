"""Weather-aware ranking for the Styling Deck: turns the current local weather
into a natural-language "ideal outfit" sentence, embeds it with the same model
used for item tags, and queries Pinecone — scoped to one user's wardrobe and one
clothing category — for the closest aesthetic matches.

This reuses embeddings._get_model()/_get_index() rather than re-instantiating
either (loading the MiniLM model is the slow part of this service — see
agent_docs/code_patterns.md "Reuse existing modules before creating new
abstractions"). Mirrors the prose-over-key:value rationale documented in
embeddings._tags_to_text: semantic embedding models match a descriptive
sentence against item descriptions far better than raw temperature numbers.
"""

from typing import Literal

from app.services.embeddings import _get_index, _get_model
from app.services.weather import CurrentWeather

Category = Literal["top", "bottom", "shoes"]
_CATEGORIES: tuple[Category, ...] = ("top", "bottom", "shoes")

_TOP_K = 20


def _weather_to_query_text(weather: CurrentWeather) -> str:
    """Render current conditions into a sentence describing the ideal outfit —
    bucketed by feel rather than exact degrees, since the embedding model
    matches aesthetic/textural descriptions, not numbers."""
    t = weather.temperature_c
    if t < 5:
        feel = "a warm, heavily insulated cold-weather outfit with thick layers"
    elif t < 12:
        feel = "a warm layered outfit suitable for chilly weather"
    elif t < 18:
        feel = "a light jacket or layered outfit for cool, mild weather"
    elif t < 24:
        feel = "a comfortable outfit for mild, pleasant weather"
    elif t < 29:
        feel = "a light, breathable outfit for warm weather"
    else:
        feel = "a minimal, lightweight, breathable outfit for hot weather"

    if weather.condition in ("rainy", "drizzling", "showery", "stormy"):
        feel += ", with water-resistant or technical textures for wet conditions"
    elif weather.condition == "snowy":
        feel += ", with insulated, weatherproof pieces for snow"

    return feel


def recommend_items(user_id: str, weather: CurrentWeather) -> dict[Category, list[str]]:
    """Return each category's item IDs ranked by aesthetic match to the current
    weather, most-recommended first. Categories with no items in the user's
    wardrobe come back as empty lists — the frontend falls back to its default
    (most-recent-first) ordering for those."""
    text = _weather_to_query_text(weather)
    vector = _get_model().encode(text, normalize_embeddings=True).tolist()
    index = _get_index()

    ranked: dict[Category, list[str]] = {}
    for category in _CATEGORIES:
        result = index.query(
            vector=vector,
            top_k=_TOP_K,
            filter={"user_id": {"$eq": user_id}, "category": {"$eq": category}},
            include_metadata=False,
        )
        ranked[category] = [match.id for match in result.matches]

    return ranked
