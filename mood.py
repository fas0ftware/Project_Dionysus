"""Weather-to-music engine for Dionysus (no Streamlit or network dependency).

v2 looks at more than the sky: temperature, wind and whether the sun is up at
the city's local time all shape the mood and the songs that are picked.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from urllib.parse import quote

# Format: (Mood Text, Song Name, Artist, Genre)
PLAYLISTS = {
    "clear": [
        ("Sunny & Bright", "Happy", "Pharrell Williams", "Pop"),
        ("Golden Vibes", "Walking On Sunshine", "Katrina & The Waves", "80s Pop"),
        ("Energetic Sun", "Can't Stop the Feeling!", "Justin Timberlake", "Pop"),
        ("Good Day", "Lovely Day", "Bill Withers", "Soul"),
        ("Summer Breeze", "Watermelon Sugar", "Harry Styles", "Pop"),
        ("Blue Skies", "Here Comes the Sun", "The Beatles", "Classic Rock"),
        ("Bright Side", "Good as Hell", "Lizzo", "Pop"),
    ],
    "clear_night": [
        ("Starlit", "Starboy", "The Weeknd ft. Daft Punk", "R&B"),
        ("Moonlight", "Fly Me to the Moon", "Frank Sinatra", "Jazz"),
        ("Night Drive", "Nightcall", "Kavinsky", "Synthwave"),
        ("Clear Night", "Clair de Lune", "Claude Debussy", "Classical"),
        ("City Lights", "Blinding Lights", "The Weeknd", "Synth-Pop"),
    ],
    "clouds": [
        ("Cloudy Vibes", "Sweater Weather", "The Neighbourhood", "Indie"),
        ("Grey Skies", "Team", "Lorde", "Alt-Pop"),
        ("Chill Clouds", "Cardigan", "Taylor Swift", "Folk"),
        ("Soft Mood", "Video Games", "Lana Del Rey", "Baroque Pop"),
        ("Overcast", "Midnight City", "M83", "Electronic"),
        ("Drifting", "Holocene", "Bon Iver", "Indie Folk"),
    ],
    "mist": [
        ("Misty Dream", "Teardrop", "Massive Attack", "Trip-Hop"),
        ("Foggy Mind", "Intro", "The xx", "Indie"),
        ("Haze", "Svefn-g-englar", "Sigur Rós", "Post-Rock"),
        ("Low Visibility", "Breathe", "Télépopmusik", "Downtempo"),
    ],
    "drizzle": [
        ("Light Rain", "Banana Pancakes", "Jack Johnson", "Acoustic"),
        ("Soft Drops", "The Night We Met", "Lord Huron", "Indie Folk"),
        ("Drizzle Days", "Riptide", "Vance Joy", "Indie Pop"),
    ],
    "rain": [
        ("Melancholic Rain", "Set Fire to the Rain", "Adele", "Soul/Pop"),
        ("Rainy Jazz", "Don't Know Why", "Norah Jones", "Jazz"),
        ("Emotional", "Fix You", "Coldplay", "Rock"),
        ("Stormy Heart", "Grenade", "Bruno Mars", "Pop"),
        ("Raindrops", "Stan", "Eminem ft. Dido", "Hip-Hop"),
        ("Purple Rain", "Purple Rain", "Prince", "Rock"),
    ],
    "snow": [
        ("Snowy Silence", "Let It Snow!", "Frank Sinatra", "Classic Jazz"),
        ("Winter Magic", "White Christmas", "Bing Crosby", "Classic"),
        ("Cold Comfort", "Winter Winds", "Mumford & Sons", "Folk"),
        ("Frozen Air", "Holocene", "Bon Iver", "Indie Folk"),
    ],
    "thunderstorm": [
        ("Stormy Power", "Thunderstruck", "AC/DC", "Hard Rock"),
        ("Dark Energy", "Believer", "Imagine Dragons", "Rock"),
        ("Electric", "Immigrant Song", "Led Zeppelin", "Classic Rock"),
        ("Riders", "Riders on the Storm", "The Doors", "Psychedelic Rock"),
    ],
    "hot": [
        ("Heatwave", "Heat Waves", "Glass Animals", "Indie Pop"),
        ("Hot Hot Hot", "Hot in Herre", "Nelly", "Hip-Hop"),
        ("Summer Heat", "Summertime", "DJ Jazzy Jeff & The Fresh Prince", "Hip-Hop"),
    ],
    "freezing": [
        ("Deep Freeze", "Cold as Ice", "Foreigner", "Rock"),
        ("Ice Cold", "Ice Ice Baby", "Vanilla Ice", "Hip-Hop"),
        ("Frostbite", "Cold Little Heart", "Michael Kiwanuka", "Soul"),
    ],
    "windy": [
        ("Windswept", "Wind of Change", "Scorpions", "Rock"),
        ("Gusty", "Blowin' in the Wind", "Bob Dylan", "Folk"),
        ("Free Spirit", "Dust in the Wind", "Kansas", "Rock"),
    ],
    # Used for unknown conditions
    "default": [
        ("Chill Mode", "Three Little Birds", "Bob Marley", "Reggae"),
        ("Relax", "Weightless", "Marconi Union", "Ambient"),
        ("Easy Going", "Sunday Morning", "Maroon 5", "Pop"),
    ],
}

# OpenWeatherMap "main" values that share a pool with another category.
WEATHER_ALIASES = {
    "fog": "mist",
    "haze": "mist",
    "smoke": "mist",
    "dust": "mist",
    "sand": "mist",
    "ash": "mist",
    "squall": "thunderstorm",
    "tornado": "thunderstorm",
}

HOT_C = 30.0
FREEZING_C = -2.0
WINDY_MS = 10.0  # about 36 km/h, a "fresh breeze" or stronger


@dataclass(frozen=True)
class Track:
    mood: str
    song: str
    artist: str
    genre: str

    @property
    def spotify_url(self) -> str:
        return spotify_search_url(self.song, self.artist)

    @property
    def youtube_url(self) -> str:
        return "https://www.youtube.com/results?search_query=" + quote(f"{self.song} {self.artist}", safe="")


@dataclass(frozen=True)
class WeatherContext:
    city: str
    country: str
    condition: str      # OpenWeatherMap "main", e.g. "Rain"
    description: str    # e.g. "light rain"
    temp_c: float
    feels_like_c: float
    humidity: int
    wind_ms: float
    is_night: bool
    icon: str = ""

    @property
    def temp_f(self) -> float:
        return self.temp_c * 9 / 5 + 32


def context_from_owm(data: dict) -> WeatherContext:
    """Build a WeatherContext from an OpenWeatherMap /weather response (metric units)."""
    weather = (data.get("weather") or [{}])[0]
    main = data.get("main", {})
    sys_ = data.get("sys", {})
    now = data.get("dt")
    sunrise, sunset = sys_.get("sunrise"), sys_.get("sunset")
    if None not in (now, sunrise, sunset):
        is_night = not (sunrise <= now < sunset)
    else:  # OWM icons end in "n" at night
        is_night = str(weather.get("icon", "")).endswith("n")
    return WeatherContext(
        city=str(data.get("name", "")),
        country=str(sys_.get("country", "")),
        condition=str(weather.get("main", "Unknown")),
        description=str(weather.get("description", "")),
        temp_c=float(main.get("temp", 0.0)),
        feels_like_c=float(main.get("feels_like", main.get("temp", 0.0))),
        humidity=int(main.get("humidity", 0)),
        wind_ms=float(data.get("wind", {}).get("speed", 0.0)),
        is_night=is_night,
        icon=str(weather.get("icon", "")),
    )


def pool_key(condition: str, is_night: bool = False) -> str:
    key = condition.lower()
    key = WEATHER_ALIASES.get(key, key)
    if key not in PLAYLISTS:
        key = "default"
    if key == "clear" and is_night:
        key = "clear_night"
    return key


def mood_label(ctx: WeatherContext) -> str:
    """Short human label combining sky, temperature, wind and time of day."""
    parts = []
    if ctx.feels_like_c >= HOT_C:
        parts.append("Scorching")
    elif ctx.feels_like_c <= FREEZING_C:
        parts.append("Frozen")
    if ctx.wind_ms >= WINDY_MS:
        parts.append("Windswept")
    sky = {
        "clear": "Sunny", "clear_night": "Starry", "clouds": "Cloudy", "mist": "Misty",
        "drizzle": "Drizzly", "rain": "Rainy", "snow": "Snowy", "thunderstorm": "Stormy",
    }.get(pool_key(ctx.condition, ctx.is_night), "Easy")
    parts.append(sky)
    parts.append("Night" if ctx.is_night else "Day")
    return " ".join(parts)


def recommend(ctx: WeatherContext, n: int = 3, rng=random) -> list[Track]:
    """Return n distinct tracks. The sky decides most of them; extreme heat,
    cold or wind contribute one track from their own pool."""
    main_pool = list(PLAYLISTS[pool_key(ctx.condition, ctx.is_night)])
    extra_pool = []
    if ctx.feels_like_c >= HOT_C:
        extra_pool += PLAYLISTS["hot"]
    elif ctx.feels_like_c <= FREEZING_C:
        extra_pool += PLAYLISTS["freezing"]
    if ctx.wind_ms >= WINDY_MS:
        extra_pool += PLAYLISTS["windy"]

    picks: list[tuple] = []
    if extra_pool and n > 1:
        picks.append(rng.choice(extra_pool))
    remaining = [t for t in main_pool if t not in picks]
    rng.shuffle(remaining)
    picks += remaining[: max(0, n - len(picks))]
    if len(picks) < n:  # tiny pool: top up from default
        picks += [t for t in PLAYLISTS["default"] if t not in picks][: n - len(picks)]
    return [Track(*t) for t in picks[:n]]


def spotify_search_url(song: str, artist: str) -> str:
    """Spotify search link for a song. A search link always resolves, unlike a
    hard-coded track ID that can silently go stale or be mistyped."""
    return "https://open.spotify.com/search/" + quote(f"{song} {artist}", safe="")


def recommend_song(weather_main: str, rng=random):
    """v1-compatible helper: pick one song for a weather condition.

    Returns (mood, song, artist, genre, spotify_link).
    """
    mood, song, artist, genre = rng.choice(PLAYLISTS[pool_key(weather_main)])
    return mood, song, artist, genre, spotify_search_url(song, artist)
