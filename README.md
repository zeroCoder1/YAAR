# YAAR - Your App Analytics Reviews 📱🔍

YAAR is a web-based tool that scrapes user reviews from the **Google Play Store** and **Apple App Store**, 
allowing you to filter, analyze, and visualize reviews across platforms with beautiful word clouds and intuitive filters.

Built for product teams, indie developers, and analysts who want real insights — without bloated dashboards.

---

## 🚀 Features

- Scrape **Play Store** (Android) and **App Store** (iOS) reviews
- **Filter** reviews by:
  - Platform (Android/iOS)
  - Star Rating (1–5 stars)
  - Keyword / Word
- **Smart Word Cloud**:
  - Filters junk words like "the", "and", "to"
  - Smooth animated transitions
  - Click on a word to filter reviews by that word
- **Retain** all filter selections while exploring
- **Clear Filters** easily with one click
- Scrapes up to **300 latest reviews** per platform
- Supports selecting **Play Store country** for scraping localized reviews
- Designed for hosting on **Railway**, **Vercel**, or any server

---

## 🛠 Tech Stack

- Backend: [FastAPI](https://fastapi.tiangolo.com/)
- Frontend: [D3.js](https://d3js.org/) for word cloud
- Scrapers:
  - [google-play-scraper](https://pypi.org/project/google-play-scraper/) (Playstore)
  - Official [Apple iTunes RSS API](https://rss.itunes.apple.com/) (Appstore)
- Hosted using [Uvicorn](https://www.uvicorn.org/)

---

## 🏗️ Build Locally

- Create project folder and enter it
mkdir yaar && cd yaar

- Create Python virtual environment
```python3 -m venv venv```
```source venv/bin/activate```

- Install dependencies
```pip install requirements```
or
```pip install fastapi uvicorn jinja2 google-play-scraper python-multipart requests d3-cloud```

- Start the FastAPI server
```uvicorn main:app --reload --host 0.0.0.0 --port 8000```

---
## 📺 Live
https://yaar.onrender.com/
