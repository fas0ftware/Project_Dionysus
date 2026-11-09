import os

import streamlit as st
from dotenv import load_dotenv

from mood import recommend_song
from weather import fetch_weather

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

st.set_page_config(page_title="Dionysus | Skybeat", page_icon="🎵", layout="centered")

MAJOR_CITIES = [
    "Select a City...", "Istanbul", "Izmir", "Ankara", "London", "New York",
    "Tokyo", "Paris", "Berlin", "Moscow", "Dubai", "Singapore",
    "Los Angeles", "Barcelona", "Rome", "Amsterdam"
]

# --- BRANDING ---
st.markdown(
    """
    <div style='text-align: center; padding-top: 10px; padding-bottom: 20px;'>
        <h1 style='font-size: 70px; font-weight: 800; letter-spacing: 4px; color: #FF4B4B; margin-bottom: 0; text-shadow: 2px 2px 8px rgba(0,0,0,0.3);'>DIONYSUS</h1>
        <h2 style='font-size: 30px; font-weight: 300; letter-spacing: 8px; color: #E0E0E0; margin-top: -10px; text-transform: uppercase;'>SKYBEAT</h2>
        <div style="width: 50px; height: 3px; background-color: #FF4B4B; margin: 10px auto;"></div>
    </div>
    """,
    unsafe_allow_html=True
)


# --- FRONTEND UI ---
def main():
    col1, col2 = st.columns([3, 1])
    with col1:
        option = st.selectbox("Select Destination:", MAJOR_CITIES + ["Custom Search"], label_visibility="collapsed")
        if option == "Custom Search":
            city = st.text_input("Enter City:", placeholder="Type city name...")
        else:
            city = option if option != "Select a City..." else ""
    with col2:
        st.write("")
        if option == "Custom Search":
            st.write("")
        btn = st.button("SCAN SKY", use_container_width=True)

    city = city.strip()

    if btn and not city:
        st.info("Pick a city from the list or type one first.")

    if btn and city:
        with st.spinner('Accessing satellite data...'):
            data, error = fetch_weather(city, API_KEY)

        if error:
            st.error(error)
            return

        main_weather = data['weather'][0]['main']
        desc = data['weather'][0]['description'].title()
        temp = data['main']['temp']

        mood, song, artist, genre, link = recommend_song(main_weather)

        # UI Result Card
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Location", city.upper())
        c2.metric("Condition", desc)
        c3.metric("Temp", f"{temp:.1f}°C")

        st.success(f"Detected Mood: **{mood}**")

        # Music Card
        with st.container():
            st.markdown(f"""
            <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; text-align: center;">
                <h3 style="color: #FF4B4B; margin:0;">Now Playing</h3>
                <p style="font-size: 24px; margin: 10px 0; font-weight: bold;">{song}</p>
                <p style="color: gray; font-size: 16px;">by {artist} • {genre}</p>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            st.link_button("▶ Find on Spotify", link, use_container_width=True)


if __name__ == "__main__":
    main()
