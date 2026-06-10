import numpy as np
import pytest

from app.services import recommendations
from app.services.recommendations import _weather_to_query_text, recommend_items
from app.services.weather import CurrentWeather


@pytest.mark.parametrize(
    ("temperature_c", "expected_phrase"),
    [
        (-5, "heavily insulated cold-weather"),
        (8, "warm layered outfit suitable for chilly weather"),
        (15, "light jacket or layered outfit for cool, mild weather"),
        (21, "comfortable outfit for mild, pleasant weather"),
        (26, "light, breathable outfit for warm weather"),
        (32, "minimal, lightweight, breathable outfit for hot weather"),
    ],
)
def test_weather_to_query_text_buckets_by_temperature(temperature_c, expected_phrase):
    text = _weather_to_query_text(CurrentWeather(temperature_c=temperature_c, condition="clear"))

    assert expected_phrase in text


@pytest.mark.parametrize("condition", ["rainy", "drizzling", "showery", "stormy"])
def test_weather_to_query_text_adds_wet_weather_modifier(condition):
    text = _weather_to_query_text(CurrentWeather(temperature_c=15, condition=condition))

    assert "water-resistant or technical textures" in text


def test_weather_to_query_text_adds_snow_modifier():
    text = _weather_to_query_text(CurrentWeather(temperature_c=-2, condition="snowy"))

    assert "insulated, weatherproof pieces for snow" in text


def test_weather_to_query_text_clear_has_no_modifier():
    text = _weather_to_query_text(CurrentWeather(temperature_c=20, condition="clear"))

    assert "water-resistant" not in text
    assert "snow" not in text


class _FakeMatch:
    def __init__(self, item_id):
        self.id = item_id


class _FakeIndex:
    def __init__(self, results_by_category):
        self._results_by_category = results_by_category
        self.queries = []

    def query(self, *, vector, top_k, filter, include_metadata):
        self.queries.append(filter)
        category = filter["category"]["$eq"]
        ids = self._results_by_category.get(category, [])
        return type("Result", (), {"matches": [_FakeMatch(i) for i in ids]})()


def test_recommend_items_queries_each_category_scoped_to_user(monkeypatch):
    fake_index = _FakeIndex({"top": ["top-1", "top-2"], "bottom": ["bottom-1"], "shoes": []})

    monkeypatch.setattr(
        recommendations,
        "_get_model",
        lambda: type("M", (), {"encode": lambda self, *a, **k: np.zeros(384)})(),
    )
    monkeypatch.setattr(recommendations, "_get_index", lambda: fake_index)

    weather = CurrentWeather(temperature_c=20, condition="clear")
    ranked = recommend_items("user-123", weather)

    assert ranked == {"top": ["top-1", "top-2"], "bottom": ["bottom-1"], "shoes": []}
    assert {q["category"]["$eq"] for q in fake_index.queries} == {"top", "bottom", "shoes"}
    assert all(q["user_id"]["$eq"] == "user-123" for q in fake_index.queries)
