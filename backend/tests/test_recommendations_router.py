from app.routers import recommendations
from app.services.weather import CurrentWeather, WeatherError


def test_recommendations_success(client, monkeypatch):
    monkeypatch.setattr(
        recommendations, "get_current_weather", lambda lat, lon: CurrentWeather(18.0, "overcast")
    )
    monkeypatch.setattr(
        recommendations,
        "recommend_items",
        lambda user_id, weather: {"top": ["t1"], "bottom": ["b1"], "shoes": []},
    )

    response = client.get(
        "/recommendations", params={"user_id": "user-123", "latitude": 37.5, "longitude": -122.4}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["temperature_c"] == 18.0
    assert body["condition"] == "overcast"
    assert body["ranked_item_ids"] == {"top": ["t1"], "bottom": ["b1"], "shoes": []}


def test_recommendations_weather_failure_returns_502(client, monkeypatch):
    def _raise(lat, lon):
        raise WeatherError("open-meteo down")

    monkeypatch.setattr(recommendations, "get_current_weather", _raise)

    response = client.get(
        "/recommendations", params={"user_id": "user-123", "latitude": 37.5, "longitude": -122.4}
    )

    assert response.status_code == 502


def test_recommendations_ranking_failure_returns_502(client, monkeypatch):
    monkeypatch.setattr(
        recommendations, "get_current_weather", lambda lat, lon: CurrentWeather(18.0, "overcast")
    )

    def _raise(user_id, weather):
        raise RuntimeError("pinecone down")

    monkeypatch.setattr(recommendations, "recommend_items", _raise)

    response = client.get(
        "/recommendations", params={"user_id": "user-123", "latitude": 37.5, "longitude": -122.4}
    )

    assert response.status_code == 502


def test_recommendations_rejects_out_of_range_latitude(client):
    response = client.get(
        "/recommendations", params={"user_id": "user-123", "latitude": 999, "longitude": 0}
    )

    assert response.status_code == 422


def test_recommendations_requires_user_id(client):
    response = client.get("/recommendations", params={"latitude": 37.5, "longitude": -122.4})

    assert response.status_code == 422
