import streamlit as st
import requests
import os
import random  # Rastgele seçim için kütüphane eklendi
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

st.set_page_config(page_title="Skybeat | Aesthesius", page_icon="🎵", layout="centered")

# --- DATA: PLAYLIST POOLS ---
# Her hava durumu için çoklu şarkı seçenekleri
# Format: (Mood Text, Song Name, Artist, Genre, Spotify Link)
PLAYLISTS = {
    "clear": [
        ("Sunny & Bright", "Happy", "Pharrell Williams", "Pop", "https://open.spotify.com/track/60nZcImufyMA1KT4e90KQv"),
        ("Golden Vibes", "Walking On Sunshine", "Katrina & The Waves", "80s Pop", "https://open.spotify.com/track/05wIrZSwuaVWhcv5FfqeH0"),
        ("Energetic Sun", "Can't Stop the Feeling!", "Justin Timberlake", "Pop", "https://open.spotify.com/track/1WkMMavIMc4JZ8cfMmxHkI"),
        ("Good Day", "Lovely Day", "Bill Withers", "Soul", "https://open.spotify.com/track/0bRXwKfigvpKZUurwqAlEh"),
        ("Summer Breeze", "Watermelon Sugar", "Harry Styles", "Pop", "https://open.spotify.com/track/6UelLqGlWMcVWRZuZz6wQe"),
    ],
    "clouds": [
        ("Cloudy Vibes", "Sweater Weather", "The Neighbourhood", "Indie", "https://open.spotify.com/track/2QjOHCTQ1Jl3zawyYOpxh6"),
        ("Grey Skies", "Team", "Lorde", "Alt-Pop", "https://open.spotify.com/track/3G6hD9BdiYigko74HK86kR"),
        ("Chill Clouds", "Cardigan", "Taylor Swift", "Folk", "https://open.spotify.com/track/4R2kfaDFhslZwpwIaKuVN5"),
        ("Soft Mood", "Video Games", "Lana Del Rey", "Baroque Pop", "https://open.spotify.com/track/241P8hryM5QU1hH7MPq9F7"),
        ("Overcast", "Midnight City", "M83", "Electronic", "https://open.spotify.com/track/1eyzqe2QqGZUmfcPZtrIyt"),
    ],
    "rain": [
        ("Melancholic Rain", "Set Fire to the Rain", "Adele", "Soul/Pop", "https://open.spotify.com/track/73R6fgvOpsnCMviF8IwyV"),
        ("Rainy Jazz", "Don't Know Why", "Norah Jones", "Jazz", "https://open.spotify.com/track/6ybViy2qrO9sIi41EgRJgx"),
        ("Emotional", "Fix You", "Coldplay", "Rock", "https://open.spotify.com/track/7LVHVU3tWfcxj5aiPFEW4Q"),
        ("Stormy Heart", "Grenade", "Bruno Mars", "Pop", "https://open.spotify.com/track/2QjOHCTQ1Jl3zawyYOpxh6"),
        ("Raindrops", "Stan", "Eminem ft. Dido", "Hip-Hop", "https://open.spotify.com/track/3UmaczJjbHGh7Lb07s8rhI"),
    ],
    "snow": [
        ("Snowy Silence", "Let It Snow!", "Frank Sinatra", "Classic Jazz", "https://open.spotify.com/track/4kKdvXD0ez7jp1296JkWts"),
        ("Winter Magic", "White Christmas", "Bing Crosby", "Classic", "https://open.spotify.com/track/4so0WskIBSktRLv9gJoEbE"),
        ("Cold Comfort", "Winter Winds", "Mumford & Sons", "Folk", "https://open.spotify.com/track/5cG2n3lZ35Z1H7Q5w10000"),
    ],
    "thunderstorm": [
        ("Stormy Power", "Thunderstruck", "AC/DC", "Hard Rock", "https://open.spotify.com/track/57bgtoPSgt236HzfBOd8kj"),
        ("Dark Energy", "Believer", "Imagine Dragons", "Rock", "https://open.spotify.com/track/0pqnGHJpmpxLKifKRmU6WP"),
        ("Electric", "Immigrant Song", "Led Zeppelin", "Classic Rock", "https://open.spotify.com/track/78lgmZwycJ3nzsdgmPPGNx"),
    ],
    # Varsayılan / Bilinmeyen durumlar için
    "default": [
        ("Chill Mode", "Three Little Birds", "Bob Marley", "Reggae", "https://open.spotify.com/track/6A9mNKZG2FwvTOMFt5m9q"),
        ("Relax", "Weightless", "Marconi Union", "Ambient", "https://open.spotify.com/track/6kkwzB6hXLIONkEk9JciA6"),
    ]
}

MAJOR_CITIES = [
    "Select a City...", "Istanbul", "Izmir", "Ankara", "London", "New York", 
    "Tokyo", "Paris", "Berlin", "Moscow", "Dubai", "Singapore", 
    "Los Angeles", "Barcelona", "Rome", "Amsterdam"
]

# --- BRANDING ---
st.markdown(
    """
    <div style='text-align: center; padding-top: 10px; padding-bottom: 20px;'>
        <h1 style='font-size: 70px; font-weight: 800; letter-spacing: 4px; color: #FF4B4B; margin-bottom: 0; text-shadow: 2px 2px 8px rgba(0,0,0,0.3);'>AESTHESIUS</h1>
        <h2 style='font-size: 30px; font-weight: 300; letter-spacing: 8px; color: #E0E0E0; margin-top: -10px; text-transform: uppercase;'>SKYBEAT</h2>
        <div style="width: 50px; height: 3px; background-color: #FF4B4B; margin: 10px auto;"></div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- BACKEND FUNCTIONS ---
def get_weather(city_name):
    # 1. API Anahtarı Kontrolü
    if not API_KEY:
        print("❌ HATA: API Anahtarı (.env) okunamadı!")
        st.error("SYSTEM ERROR: API Key missing.")
        return None

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": API_KEY, "units": "metric", "lang": "en"}
    
    try:
        print(f"🔍 İSTEK GÖNDERİLİYOR: {city_name}...") # Terminale yazar
        response = requests.get(base_url, params=params)
        
        # 2. Durum Kodunu Yazdır (En Önemli Kısım)
        print(f"📡 API CEVABI (Status Code): {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Veri başarıyla alındı.")
            return response.json()
        elif response.status_code == 401:
            print("⛔ HATA: 401 Unauthorized (API Anahtarı Yanlış veya Aktif Değil)")
            st.error("HATA: API Anahtarı geçersiz (401).")
            return None
        elif response.status_code == 404:
            print("❌ HATA: 404 Not Found (Şehir bulunamadı)")
            return None
        else:
            print(f"⚠️ HATA: Beklenmedik durum ({response.status_code})")
            return None
    except Exception as e:
        print(f"🔥 KRİTİK HATA: {e}")
        return None
def recommend_song(weather_main):
    weather_main = weather_main.lower()
    
    # İlgili hava durumu listesini al, yoksa 'default' listeyi al
    # Drizzle ve Mist gibi az rastlanan durumları ana kategorilere bağlayalım:
    if weather_main in ["drizzle", "mist", "fog", "haze"]:
        weather_main = "clouds"
    
    song_list = PLAYLISTS.get(weather_main, PLAYLISTS["default"])
    
    # Listeden RASTGELE bir şarkı seç
    return random.choice(song_list)

# --- FRONTEND UI ---
def main():
    col1, col2 = st.columns([3, 1])
    with col1:
        option = st.selectbox("Select Destination:", MAJOR_CITIES + ["Custom Search"], label_visibility="collapsed")
        city = st.text_input("Enter City:", placeholder="Type city name...") if option == "Custom Search" else (option if option != "Select a City..." else "")
    with col2:
        st.write("")
        if option == "Custom Search": st.write("") 
        btn = st.button("SCAN SKY", use_container_width=True)

    if btn and city:
        with st.spinner('Accessing satellite data...'):
            data = get_weather(city)
            if data:
                main_weather = data['weather'][0]['main']
                desc = data['weather'][0]['description'].title()
                temp = data['main']['temp']
                
                # Fonksiyondan rastgele şarkıyı al
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
                    st.link_button(f"▶ Play on Spotify", link, use_container_width=True)
            else:
                st.error("City not found. Please try again.")

if __name__ == "__main__":
    main()