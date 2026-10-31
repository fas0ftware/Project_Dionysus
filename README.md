# Dionysus | Weather Music Mood Engine

A Streamlit app that reads the live weather of any city and suggests a musical mood to match the atmosphere.

## ◼ Overview

**Dionysus** analyzes real-time weather conditions for cities around the world and maps them to a musical mood and genres. Rain, mist or clear skies each get their own sound.

## ◼ Features

- **Real-time weather:** Fetches live data from the OpenWeatherMap API.
- **Mood detection:** Maps weather conditions (mist, rain, clear and others) to musical genres.
- **City search:** Built-in list of major world cities, plus search for any city you type.
- **Safe key handling:** The API key is read from an environment variable and never stored in the code.

## ◼ Project structure

```
Project_Dionysus/
├── app.py            # Streamlit app
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

Open `.env` and set your key. Never commit the `.env` file: it holds your secret and must stay in `.gitignore`.

## ◼ Usage

```bash
streamlit run app.py
```

The app opens in your default browser. Pick a city or type your own.

## ◼ Notes and limitations

- A new OpenWeatherMap key can take a short while to become active after you create it.
- The free API plan has request limits, so avoid very frequent refreshes.
- Recommendations are based on weather mood mapping, not on personal listening history.

---

Part of the **FA Software** projects.
