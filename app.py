"""Dionysus | Skybeat - Streamlit UI."""

import html
import os

import streamlit as st
from dotenv import load_dotenv

from mood import context_from_owm, mood_label, recommend
from weather import clean_city, demo_weather, fetch_weather

__version__ = "2.0.0"

# --- CONFIGURATION ---
load_dotenv()


def get_api_key():
    key = os.getenv("OPENWEATHER_API_KEY")
    if key:
        return key
    try:  # Streamlit Community Cloud stores secrets here
        return st.secrets.get("OPENWEATHER_API_KEY")
    except Exception:
        return None


API_KEY = get_api_key()
DEMO = os.getenv("DIONYSUS_DEMO") == "1" or not API_KEY

st.set_page_config(page_title="Dionysus | Skybeat", page_icon="🎵", layout="centered")

MAJOR_CITIES = [
    "Istanbul", "Izmir", "Ankara", "London", "New York", "Tokyo", "Paris", "Berlin",
    "Moscow", "Dubai", "Singapore", "Los Angeles", "Barcelona", "Rome", "Amsterdam",
    "Reykjavik", "Cairo", "Sydney", "Rio de Janeiro", "Oslo",
]
CUSTOM = "Custom search..."
SHORT_SKY = {"Thunderstorm": "Storm", "Tornado": "Storm", "Squall": "Squall"}

ICONS = {"01": "☀️", "02": "🌤️", "03": "⛅", "04": "☁️", "09": "🌦️", "10": "🌧️",
         "11": "⛈️", "13": "❄️", "50": "🌫️"}


@st.cache_data(ttl=600, show_spinner=False)
def cached_weather(city: str, demo: bool):
    """Cache each city for 10 minutes so repeated scans do not burn API quota."""
    if demo:
        return demo_weather(city), None
    return fetch_weather(city, API_KEY)


# --- BRANDING ---
st.markdown(
    """
    <div style='text-align: center; padding-top: 10px; padding-bottom: 20px;'>
        <h1 style='font-size: 70px; font-weight: 800; letter-spacing: 4px; color: #FF4B4B; margin-bottom: 0; text-shadow: 2px 2px 8px rgba(0,0,0,0.3);'>DIONYSUS</h1>
        <h2 style='font-size: 30px; font-weight: 300; letter-spacing: 8px; color: #E0E0E0; margin-top: -10px; text-transform: uppercase;'>SKYBEAT</h2>
        <div style="width: 50px; height: 3px; background-color: #FF4B4B; margin: 10px auto;"></div>
    </div>
    """,
    unsafe_allow_html=True,
)


def track_card(track) -> str:
    e = html.escape
    return f"""
    <div style="background-color:#1E1E1E;padding:16px 20px;border-radius:10px;border:1px solid #333;margin-bottom:10px;">
        <div style="color:#FF4B4B;font-size:12px;letter-spacing:2px;text-transform:uppercase;">{e(track.mood)}</div>
        <div style="font-size:20px;font-weight:bold;margin:4px 0;color:#F5F5F5;">{e(track.song)}</div>
        <div style="color:gray;font-size:14px;">by {e(track.artist)} • {e(track.genre)}</div>
    </div>"""


# --- FRONTEND UI ---
def main():
    if DEMO:
        st.info("Demo mode: showing sample weather data. Add OPENWEATHER_API_KEY to `.env` for live data.",
                icon="🧪")

    col1, col2 = st.columns([3, 1])
    with col1:
        option = st.selectbox("Destination", MAJOR_CITIES + [CUSTOM], index=None,
                              placeholder="Select a city...", label_visibility="collapsed")
        city = st.text_input("City", placeholder="Type a city, e.g. Kyoto or Paris,FR") \
            if option == CUSTOM else (option or "")
    with col2:
        btn = st.button("SCAN SKY", width="stretch", type="primary")

    unit = st.radio("Units", ["°C", "°F"], horizontal=True, label_visibility="collapsed",
                    index=1 if st.query_params.get("unit") == "F" else 0)
    city = city.strip()

    # Shareable links: ?city=Tokyo (&unit=F) scans straight away.
    shared = st.query_params.get("city", "")
    if not btn and not city and shared:
        city, btn = shared.strip(), True

    if btn and not city:
        st.info("Pick a city from the list or type one first.")
        return
    if not (btn and city):
        return
    if clean_city(city) is None:
        st.error("That does not look like a city name. Use letters, spaces and hyphens only.")
        return
    city = clean_city(city)
    st.query_params["city"] = city

    with st.spinner("Accessing satellite data..."):
        data, error = cached_weather(city, DEMO)
    if error:
        st.error(error)
        return

    ctx = context_from_owm(data)
    tracks = recommend(ctx, n=3)

    def fmt(t_c):
        return f"{t_c:.1f}°C" if unit == "°C" else f"{t_c * 9 / 5 + 32:.1f}°F"

    st.markdown("---")
    icon = ICONS.get(ctx.icon[:2], "🌍")
    place = ctx.city.upper() + (f", {ctx.country}" if ctx.country else "")
    c1, c2, c3, c4 = st.columns([1.25, 1.35, 1, 1])
    c1.metric("Location", place)
    c2.metric("Sky", f"{icon} {SHORT_SKY.get(ctx.condition, ctx.condition)}", ctx.description.capitalize(), delta_color="off", delta_arrow="off")
    c3.metric("Temp", fmt(ctx.temp_c), f"feels {fmt(ctx.feels_like_c)}", delta_color="off", delta_arrow="off")
    c4.metric("Wind", f"{ctx.wind_ms:.1f} m/s", f"{ctx.humidity}% humidity", delta_color="off", delta_arrow="off")

    st.success(f"Detected mood: **{mood_label(ctx)}**")
    st.subheader("Now playing")
    for track in tracks:
        st.markdown(track_card(track), unsafe_allow_html=True)
        a, b = st.columns(2)
        a.link_button("▶ Spotify", track.spotify_url, width="stretch")
        b.link_button("▶ YouTube", track.youtube_url, width="stretch")

    st.caption(f"Share this result: `?city={city}`  ·  Dionysus v{__version__} · weather by OpenWeatherMap · results cached for 10 minutes")


if __name__ == "__main__":
    main()
