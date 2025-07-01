import requests
from dotenv import load_dotenv
import json
import os
import urllib.parse
from modules.logging.logger import logger

load_dotenv()


# adzuna API credentials
def fetch_jobs_adzuna(title: str, location: str = "India", country: str = "in"):
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 10,
        "what": title,
        "where": location,
        "content-type": "application/json",
        "max_days_old": 7,  # Optional: Filter jobs posted in the last 7 days
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching jobs from Adzuna: {e}")
        return {"results": []}
