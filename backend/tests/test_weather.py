import httpx
import pytest

from app.services import weather
from app.services.weather import WeatherError, get_current_weather


class _FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=self)

    def json(self):
        return self._json_data


def test_get_current_weather_maps_known_code(monkeypatch):
    monkeypatch.setattr(
        weather.httpx,
        "get",
        lambda *a, **k: _FakeResponse({"current": {"temperature_2m": 21.5, "weather_code": 3}}),
    )

    result = get_current_weather(37.5, -122.4)

    assert result.temperature_c == 21.5
    assert result.condition == "overcast"


def test_get_current_weather_unknown_code_defaults_to_clear(monkeypatch):
    monkeypatch.setattr(
        weather.httpx,
        "get",
        lambda *a, **k: _FakeResponse({"current": {"temperature_2m": 10.0, "weather_code": 1234}}),
    )

    result = get_current_weather(37.5, -122.4)

    assert result.condition == "clear"


def test_get_current_weather_raises_on_http_error(monkeypatch):
    def _raise(*a, **k):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr(weather.httpx, "get", _raise)

    with pytest.raises(WeatherError):
        get_current_weather(37.5, -122.4)


def test_get_current_weather_raises_on_malformed_response(monkeypatch):
    monkeypatch.setattr(weather.httpx, "get", lambda *a, **k: _FakeResponse({"current": {}}))

    with pytest.raises(WeatherError):
        get_current_weather(37.5, -122.4)
