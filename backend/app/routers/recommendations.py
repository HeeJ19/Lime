"""Recommendation endpoint: orchestrates the weather -> ranking half of the
Vector-Driven Recommendation Engine (the embedding/upsert half lives in the
ingestion pipeline — see app/routers/items.py).

Flow: Open-Meteo (current local weather) -> natural-language "ideal outfit"
sentence -> embed -> Pinecone query scoped to this user's wardrobe, ranked
per category. The frontend uses the ranked IDs to reorder its swipe stacks
so the most weather-appropriate item surfaces first — see agent_docs/
code_patterns.md "Frontend -> Recommendations" data-fetching flow.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.recommendations import recommend_items
from app.services.weather import WeatherError, get_current_weather

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendationResponse(BaseModel):
    temperature_c: float
    condition: str
    ranked_item_ids: dict[str, list[str]]


@router.get("", response_model=RecommendationResponse)
def get_recommendations(
    user_id: str = Query(..., min_length=1),
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
) -> RecommendationResponse:
    try:
        weather = get_current_weather(latitude, longitude)
    except WeatherError:
        raise HTTPException(
            status_code=502, detail="Couldn't fetch local weather — try again in a moment."
        )

    ranked = recommend_items(user_id, weather)

    return RecommendationResponse(
        temperature_c=weather.temperature_c,
        condition=weather.condition,
        ranked_item_ids=ranked,
    )
