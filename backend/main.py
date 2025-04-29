from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pydantic import BaseModel
import asyncio
from google_play_scraper import reviews as gp_reviews
from app_store_scraper import AppStore
import requests

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

reviews_db = []

class ScrapeRequest(BaseModel):
    playstore_bundle_id: Optional[str] = None
    appstore_id: Optional[str] = None
    country: str = "us"

@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    page: int = 1,
    platform: Optional[str] = None,
    stars: Optional[str] = None,
    word: Optional[str] = None,
    playstore_id: Optional[str] = None,
    appstore_id: Optional[str] = None
):
    filtered = reviews_db
    if platform:
        filtered = [r for r in filtered if r["platform"] == platform]
    if stars and stars.isdigit():
        filtered = [r for r in filtered if r["rating"] == int(stars)]
    if word and word.strip() != "":
        word = word.strip().lower()
        filtered = [r for r in filtered if word in r["content"].lower()]
    return templates.TemplateResponse(
    "index.html",
    {
        "request": request,
        "reviews": filtered,
        "platform": platform,
        "stars": stars,
        "word": word,
        "playstore_id": playstore_id,
        "appstore_id": appstore_id,
    }
)

@app.post("/scrape", response_class=HTMLResponse)
async def scrape(
    request: Request,
    playstore_id: str = Form(None),
    appstore_id: str = Form(None)
):
    global reviews_db
    reviews_db.clear()

    tasks = []

    if playstore_id:
        tasks.append(scrape_google_play(playstore_id))
    if appstore_id:
        tasks.append(scrape_app_store(appstore_id)) 

    await asyncio.gather(*tasks)

    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "reviews": reviews_db,
            "playstore_id": playstore_id,
            "appstore_id": appstore_id,
            "platform": None,
            "stars": None,
            "word": None,
        }
    )

@app.get("/filter", response_class=HTMLResponse)
async def filter_reviews(request: Request, platform: Optional[str] = None, stars: Optional[int] = None, word: Optional[str] = None):
    filtered = reviews_db
    if platform:
        filtered = [r for r in filtered if r["platform"] == platform]
    if stars:
        filtered = [r for r in filtered if r["rating"] == stars]
    if word:
        word = word.lower()
        filtered = [r for r in filtered if word in r["content"].lower()]
    return templates.TemplateResponse("index.html", {"request": request, "reviews": filtered})

async def scrape_google_play(bundle_id):
    result, _ = gp_reviews(
        bundle_id,
        lang='en',
        country='us',
        count=300,
    )
    for r in result:
        reviews_db.append({
            "platform": "android",
            "rating": r["score"],
            "content": r["content"],
            "date": r["at"].strftime("%Y-%m-%d") if r.get("at") else "Unknown"
        })

async def scrape_app_store(app_id: str, country: str = "us"):
    limit = 50
    offset = 0
    fetched_reviews = 0
    max_reviews = 300

    while fetched_reviews < max_reviews:
        url = f"https://itunes.apple.com/rss/customerreviews/id={app_id}/sortby=mostrecent/json?offset={offset}&limit={limit}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                entries = data.get("feed", {}).get("entry", [])
                if not entries or len(entries) <= 1:  # Only app metadata, no reviews
                    break
                for entry in entries:
                    if isinstance(entry, dict) and "im:rating" in entry:
                        reviews_db.append({
                            "platform": "ios",
                            "rating": int(entry["im:rating"]["label"]),
                            "content": entry.get("content", {}).get("label", ""),
                            "date": entry.get("updated", {}).get("label", "").split("T")[0] if "updated" in entry else "Unknown"
                        })
                        fetched_reviews += 1
                        if fetched_reviews >= max_reviews:
                            break
                offset += limit
            else:
                print(f"AppStore fetch failed at offset {offset}, status: {response.status_code}")
                break
        except Exception as e:
            print(f"Exception fetching AppStore reviews: {e}")
            break
