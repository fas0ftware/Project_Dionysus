import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mood import PLAYLISTS, recommend_song, spotify_search_url  # noqa: E402


def test_every_playlist_entry_is_well_formed():
    assert "default" in PLAYLISTS
    for key, songs in PLAYLISTS.items():
        assert songs, key
        for entry in songs:
            assert len(entry) == 4 and all(entry), (key, entry)


def test_known_condition_uses_its_pool():
    pool = {(m, s, a, g) for m, s, a, g in PLAYLISTS["rain"]}
    for seed in range(20):
        mood, song, artist, genre, _ = recommend_song("Rain", random.Random(seed))
        assert (mood, song, artist, genre) in pool


def test_aliases_map_to_clouds():
    pool = set(PLAYLISTS["clouds"])
    for name in ("Mist", "Fog", "Haze", "Drizzle"):
        mood, song, artist, genre, _ = recommend_song(name, random.Random(1))
        assert (mood, song, artist, genre) in pool


def test_unknown_condition_falls_back_to_default():
    pool = set(PLAYLISTS["default"])
    mood, song, artist, genre, _ = recommend_song("Tornado", random.Random(1))
    assert (mood, song, artist, genre) in pool


def test_spotify_link_is_encoded():
    link = spotify_search_url("Walking On Sunshine", "Katrina & The Waves")
    assert link.startswith("https://open.spotify.com/search/")
    assert " " not in link and "&" not in link.split("/search/")[1]
    assert "%26" in link


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
