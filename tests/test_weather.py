import os
import sys
from unittest import mock

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import weather  # noqa: E402


def _response(status, payload=None):
    resp = mock.Mock()
    resp.status_code = status
    resp.json.return_value = payload or {}
    return resp


OK = {"weather": [{"main": "Clear"}], "main": {"temp": 20}}


def test_missing_key_does_not_call_api():
    with mock.patch.object(weather.requests, "get") as get:
        data, error = weather.fetch_weather("Paris", None)
    assert data is None and "OPENWEATHER_API_KEY" in error
    get.assert_not_called()


def test_success_returns_json_and_uses_https_and_timeout():
    with mock.patch.object(weather.requests, "get", return_value=_response(200, OK)) as get:
        data, error = weather.fetch_weather("Paris", "key")
    assert data == OK and error is None
    url = get.call_args.args[0]
    assert url.startswith("https://")
    assert get.call_args.kwargs["timeout"] == weather.REQUEST_TIMEOUT


def test_error_statuses_have_distinct_messages():
    messages = {}
    for status in (401, 404, 429, 500):
        with mock.patch.object(weather.requests, "get", return_value=_response(status)):
            data, error = weather.fetch_weather("Paris", "key")
        assert data is None and error
        messages[status] = error
    assert len(set(messages.values())) == 4


def test_network_failure_is_reported():
    with mock.patch.object(weather.requests, "get", side_effect=requests.Timeout("slow")):
        data, error = weather.fetch_weather("Paris", "key")
    assert data is None and "unreachable" in error


def test_city_validation_blocks_junk_before_network():
    for bad in ("", "   ", "<script>", "a" * 200, "Paris; DROP", "123", "../etc"):
        with mock.patch.object(weather.requests, "get") as get:
            data, error = weather.fetch_weather(bad, "key")
        assert data is None and error, bad
        get.assert_not_called()


def test_clean_city_accepts_real_names():
    for good in ("Paris", "New York", "São Paulo", "Rio de Janeiro", "Zürich", "İzmir",
                 "St. John's", "Paris,FR", "Москва", "東京"):
        assert weather.clean_city(good) is not None, good
    assert weather.clean_city("  New   York ") == "New York"


def test_network_error_does_not_log_api_key(caplog):
    exc = requests.ConnectionError("Max retries exceeded with url: /weather?q=Paris&appid=SECRET123")
    with mock.patch.object(weather.requests, "get", side_effect=exc):
        weather.fetch_weather("Paris", "SECRET123")
    assert "SECRET123" not in caplog.text


def test_malformed_success_body_is_an_error():
    bad = _response(200)
    bad.json.side_effect = ValueError("no json")
    with mock.patch.object(weather.requests, "get", return_value=bad):
        assert weather.fetch_weather("Paris", "key")[0] is None
    with mock.patch.object(weather.requests, "get", return_value=_response(200, {"cod": 200})):
        data, error = weather.fetch_weather("Paris", "key")
    assert data is None and "incomplete" in error


def test_demo_weather_is_deterministic_and_complete():
    a = weather.demo_weather("Tokyo", now=1_700_000_000)
    assert a == weather.demo_weather("tokyo", now=1_700_000_000)
    assert a["name"] == "Tokyo" and a["weather"][0]["main"] and "temp" in a["main"]
    skies = {weather.demo_weather(c)["weather"][0]["main"] for c in
             ("Paris", "Rome", "Oslo", "Lima", "Cairo", "Tokyo", "Izmir", "Berlin", "Dubai", "Kyiv")}
    assert len(skies) >= 3
