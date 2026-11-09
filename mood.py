"""Weather-to-music mapping for Dionysus (no Streamlit or network dependency)."""

import random
from urllib.parse import quote

# Format: (Mood Text, Song Name, Artist, Genre)
PLAYLISTS = {
    "clear": [
        ("Sunny & Bright", "Happy", "Pharrell Williams", "Pop"),
        ("Golden Vibes", "Walking On Sunshine", "Katrina & The Waves", "80s Pop"),
        ("Energetic Sun", "Can't Stop the Feeling!", "Justin Timberlake", "Pop"),
        ("Good Day", "Lovely Day", "Bill Withers", "Soul"),
        ("Summer Breeze", "Watermelon Sugar", "Harry Styles", "Pop"),
    ],
    "clouds": [
        ("Cloudy Vibes", "Sweater Weather", "The Neighbourhood", "Indie"),
        ("Grey Skies", "Team", "Lorde", "Alt-Pop"),
        ("Chill Clouds", "Cardigan", "Taylor Swift", "Folk"),
        ("Soft Mood", "Video Games", "Lana Del Rey", "Baroque Pop"),
        ("Overcast", "Midnight City", "M83", "Electronic"),
    ],
    "rain": [
        ("Melancholic Rain", "Set Fire to the Rain", "Adele", "Soul/Pop"),
        ("Rainy Jazz", "Don't Know Why", "Norah Jones", "Jazz"),
        ("Emotional", "Fix You", "Coldplay", "Rock"),
        ("Stormy Heart", "Grenade", "Bruno Mars", "Pop"),
        ("Raindrops", "Stan", "Eminem ft. Dido", "Hip-Hop"),
    ],
    "snow": [
        ("Snowy Silence", "Let It Snow!", "Frank Sinatra", "Classic Jazz"),
        ("Winter Magic", "White Christmas", "Bing Crosby", "Classic"),
        ("Cold Comfort", "Winter Winds", "Mumford & Sons", "Folk"),
    ],
    "thunderstorm": [
        ("Stormy Power", "Thunderstruck", "AC/DC", "Hard Rock"),
        ("Dark Energy", "Believer", "Imagine Dragons", "Rock"),
        ("Electric", "Immigrant Song", "Led Zeppelin", "Classic Rock"),
    ],
    # Used for unknown conditions
    "default": [
        ("Chill Mode", "Three Little Birds", "Bob Marley", "Reggae"),
        ("Relax", "Weightless", "Marconi Union", "Ambient"),
    ],
}

# Rare OpenWeatherMap conditions that share a mood with a main category.
WEATHER_ALIASES = {
    "drizzle": "clouds",
    "mist": "clouds",
    "fog": "clouds",
    "haze": "clouds",
}


def spotify_search_url(song: str, artist: str) -> str:
    """Spotify search link for a song. A search link always resolves, unlike a
    hard-coded track ID that can silently go stale or be mistyped."""
    return "https://open.spotify.com/search/" + quote(f"{song} {artist}", safe="")


def recommend_song(weather_main: str, rng=random):
    """Pick a random song for a weather condition.

    Returns (mood, song, artist, genre, spotify_link).
    """
    key = weather_main.lower()
    key = WEATHER_ALIASES.get(key, key)
    mood, song, artist, genre = rng.choice(PLAYLISTS.get(key, PLAYLISTS["default"]))
    return mood, song, artist, genre, spotify_search_url(song, artist)
