"""UI tests using Streamlit's headless AppTest runner (demo mode, no network)."""
import os

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("DIONYSUS_DEMO", "1")
    monkeypatch.chdir(os.path.dirname(APP))
    at = st_testing.AppTest.from_file(APP, default_timeout=30)
    return at.run()


def test_initial_render_shows_demo_banner_and_no_results(app):
    assert not app.exception
    assert any("Demo mode" in i.value for i in app.info)
    assert not app.success


def test_scan_without_city_asks_for_one(app):
    app.button[0].click().run()
    assert any("Pick a city" in i.value for i in app.info)


def test_scan_city_shows_mood_and_three_tracks(app):
    app.selectbox[0].set_value("Tokyo")
    app.button[0].click().run()
    assert not app.exception
    assert app.success and "Detected mood" in app.success[0].value
    assert [m.label for m in app.metric] == ["Location", "Sky", "Temp", "Wind"]
    assert app.metric[0].value == "TOKYO"
    assert app.subheader[0].value == "Now playing"


def test_fahrenheit_toggle(app):
    app.selectbox[0].set_value("Oslo")
    app.radio[0].set_value("°F")
    app.button[0].click().run()
    assert app.metric[2].value.endswith("°F")


def test_custom_city_input_and_validation(app):
    app.selectbox[0].set_value("Custom search...").run()
    app.text_input[0].set_value("<script>alert(1)</script>")
    app.button[0].click().run()
    assert not app.success and "does not look like a city" in app.error[0].value
    app.text_input[0].set_value("Kyoto").run()
    app.button[0].click().run()
    assert app.metric[0].value == "KYOTO"


def test_shareable_link_scans_on_load(monkeypatch):
    monkeypatch.setenv("DIONYSUS_DEMO", "1")
    at = st_testing.AppTest.from_file(APP, default_timeout=30)
    at.query_params["city"] = "Paris"
    at.query_params["unit"] = "F"
    at.run()
    assert at.metric[0].value == "PARIS" and at.metric[2].value.endswith("°F")


def test_shareable_link_with_junk_is_rejected(monkeypatch):
    monkeypatch.setenv("DIONYSUS_DEMO", "1")
    at = st_testing.AppTest.from_file(APP, default_timeout=30)
    at.query_params["city"] = "<img src=x onerror=alert(1)>"
    at.run()
    assert not at.success and at.error
