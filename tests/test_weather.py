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


def test_missing_key_does_not_call_api():
    with mock.patch.object(weather.requests, "get") as get:
        data, error = weather.fetch_weather("Paris", None)
    assert data is None and "OPENWEATHER_API_KEY" in error
    get.assert_not_called()


def test_success_returns_json_and_uses_https_and_timeout():
    with mock.patch.object(weather.requests, "get", return_value=_response(200, {"ok": 1})) as get:
        data, error = weather.fetch_weather("Paris", "key")
    assert data == {"ok": 1} and error is None
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


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
