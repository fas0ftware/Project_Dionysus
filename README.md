# Dionysus | Weather Music Mood Engine

A Streamlit app that reads the live weather of any city and suggests a musical mood to match the atmosphere.

## ◼ Overview

**Dionysus** (shown in the app as *Skybeat*) analyzes real-time weather conditions for cities around the world and maps them to a musical mood. Rain, clouds, snow, storms or clear skies each get their own pool of songs, and every scan picks one at random.

## ◼ Features

- **Real-time weather:** Fetches live data from the OpenWeatherMap API over HTTPS, with a request timeout so the app never hangs.
- **Mood detection:** Maps weather conditions (clear, clouds, rain, snow, thunderstorm) to a mood and a song. Mist, fog, haze and drizzle count as clouds; anything unknown falls back to a relaxed default.
- **Spotify search link:** Each suggestion comes with a button that opens a Spotify search for that song and artist.
- **City search:** Built-in list of major world cities, plus search for any city you type.
- **Clear error messages:** A missing or invalid API key, an unknown city, a rate limit and a network failure each show their own message.
- **Safe key handling:** The API key is read from an environment variable and never stored in the code.

## ◼ Project structure

```
Project_Dionysus/
├── app.py            # Streamlit app (UI)
├── mood.py           # Weather condition to song mapping
├── weather.py        # OpenWeatherMap client
├── tests/            # Tests for mood.py and weather.py
├── requirements.txt  # Dependencies
├── .env.example      # Template for your API key
└── .devcontainer/    # Dev container configuration
```

## ◼ Requirements

- Python 3.9 or newer
- A free [OpenWeatherMap](https://openweathermap.org/api) API key
- An internet connection

## ◼ Installation

```bash
git clone https://github.com/fas0ftware/Project_Dionysus.git
cd Project_Dionysus
```

Create and activate a virtual environment.

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## ◼ Configuration

Copy the example file and add your OpenWeatherMap API key to it.

Linux / macOS:

```bash
cp .env.example .env
```

Windows:

```bash
copy .env.example .env
```

Open `.env` and replace the placeholder after `OPENWEATHER_API_KEY=` with your key. Never commit the `.env` file: it holds your secret and must stay in `.gitignore`.

## ◼ Usage

```bash
streamlit run app.py
```

The app opens in your default browser. Pick a city or type your own, then press **SCAN SKY**.

Run the tests (the tests also need `requests`, which is already in `requirements.txt`):

```bash
python tests/test_mood.py
python tests/test_weather.py
```

## ◼ Notes and limitations

- A new OpenWeatherMap key can take a short while to become active after you create it (you will see a 401 message until then).
- The free API plan has request limits, so avoid very frequent refreshes.
- Recommendations are based on weather mood mapping, not on personal listening history.
- The Spotify button opens a search, not a specific track, so it keeps working even if a song changes its Spotify listing.
- The song pools are small and hard-coded in `mood.py`; add your own songs there.

---

Part of the **FA Software** projects.
