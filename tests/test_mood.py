import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mood import (PLAYLISTS, WeatherContext, context_from_owm, mood_label,  # noqa: E402
                  pool_key, recommend, recommend_song, spotify_search_url)


def ctx(condition="Clear", temp=20.0, wind=2.0, night=False, feels=None):
    return WeatherContext("Paris", "FR", condition, condition.lower(), temp,
                          temp if feels is None else feels, 50, wind, night)


def test_every_playlist_entry_is_well_formed():
    assert "default" in PLAYLISTS
    for key, songs in PLAYLISTS.items():
        assert len(songs) >= 3, key
        assert len(set(songs)) == len(songs), f"duplicate in {key}"
        for entry in songs:
            assert len(entry) == 4 and all(entry), (key, entry)


def test_known_condition_uses_its_pool():
    pool = set(PLAYLISTS["rain"])
    for seed in range(20):
        mood, song, artist, genre, _ = recommend_song("Rain", random.Random(seed))
        assert (mood, song, artist, genre) in pool


@pytest.mark.parametrize("name,expected", [
    ("Mist", "mist"), ("Fog", "mist"), ("Haze", "mist"), ("Smoke", "mist"),
    ("Drizzle", "drizzle"), ("Squall", "thunderstorm"), ("Tornado", "thunderstorm"),
    ("Volcano", "default"), ("CLEAR", "clear"),
])
def test_pool_key_aliases(name, expected):
    assert pool_key(name) == expected


def test_clear_sky_at_night_uses_night_pool():
    assert pool_key("Clear", is_night=True) == "clear_night"
    assert pool_key("Rain", is_night=True) == "rain"
    tracks = recommend(ctx("Clear", night=True), n=3, rng=random.Random(3))
    assert all(tuple(vars(t).values()) in PLAYLISTS["clear_night"] for t in tracks)


def test_recommend_returns_distinct_tracks():
    for seed in range(30):
        tracks = recommend(ctx("Rain"), n=3, rng=random.Random(seed))
        assert len(tracks) == 3 and len({t.song for t in tracks}) == 3


def test_extreme_weather_adds_a_themed_track():
    hot = recommend(ctx("Clear", temp=38), n=3, rng=random.Random(1))
    assert tuple(vars(hot[0]).values()) in PLAYLISTS["hot"]
    cold = recommend(ctx("Snow", temp=-10), n=3, rng=random.Random(1))
    assert tuple(vars(cold[0]).values()) in PLAYLISTS["freezing"]
    windy = recommend(ctx("Clouds", wind=15), n=3, rng=random.Random(1))
    assert tuple(vars(windy[0]).values()) in PLAYLISTS["windy"]


def test_recommend_tops_up_when_pool_is_small():
    tracks = recommend(ctx("Clear"), n=len(PLAYLISTS["clear"]) + 2, rng=random.Random(0))
    assert len(tracks) == len(PLAYLISTS["clear"]) + 2


@pytest.mark.parametrize("kwargs,label", [
    ({"condition": "Clear"}, "Sunny Day"),
    ({"condition": "Clear", "night": True}, "Starry Night"),
    ({"condition": "Rain", "temp": 35}, "Scorching Rainy Day"),
    ({"condition": "Snow", "temp": -8, "wind": 12}, "Frozen Windswept Snowy Day"),
    ({"condition": "Tornado"}, "Stormy Day"),
    ({"condition": "Volcano"}, "Easy Day"),
])
def test_mood_label(kwargs, label):
    assert mood_label(ctx(**kwargs)) == label


def test_feels_like_drives_extremes():
    assert mood_label(ctx("Clear", temp=27, feels=31)).startswith("Scorching")


def test_context_from_owm_full_response():
    data = {
        "name": "Izmir", "dt": 1_700_000_000,
        "sys": {"country": "TR", "sunrise": 1_699_990_000, "sunset": 1_700_030_000},
        "weather": [{"main": "Clouds", "description": "broken clouds", "icon": "04d"}],
        "main": {"temp": 18.4, "feels_like": 17.9, "humidity": 63},
        "wind": {"speed": 4.1},
    }
    c = context_from_owm(data)
    assert (c.city, c.country, c.condition, c.humidity, c.wind_ms) == ("Izmir", "TR", "Clouds", 63, 4.1)
    assert c.is_night is False and round(c.temp_f, 2) == 65.12
    data["dt"] = 1_700_040_000
    assert context_from_owm(data).is_night is True


def test_context_from_owm_minimal_response_uses_icon_for_night():
    c = context_from_owm({"weather": [{"main": "Clear", "icon": "01n"}], "main": {"temp": 5}})
    assert c.is_night is True and c.feels_like_c == 5 and c.wind_ms == 0.0


def test_links_are_encoded():
    link = spotify_search_url("Walking On Sunshine", "Katrina & The Waves")
    assert link.startswith("https://open.spotify.com/search/")
    assert " " not in link and "&" not in link.split("/search/")[1] and "%26" in link
    track = recommend(ctx("Rain"), n=1, rng=random.Random(0))[0]
    assert track.youtube_url.startswith("https://www.youtube.com/results?search_query=")
    assert " " not in track.youtube_url
