"""
===============================================================================
Development History:
-------------------------------------------------------------------------------
Date        | Author           | Change Description
------------|------------------|----------------------------------------------
2025-06-10  | Harikrishnan S   | Initial implementation of fetch_jobs_adzuna functions.
2025-07-24  | Harikrishnan S   | Added doc String for fetxh_jobs_adzuna fn
                               | Added Dev history

===============================================================================
"""

import requests
from dotenv import load_dotenv
import json
import os
import urllib.parse
from modules.logging.logger import logger

load_dotenv()


# adzuna API credentials
def fetch_jobs_adzuna(title: str, location: str = "India", country: str = "in"):
    """
    Fetches job listings from the Adzuna Job Search API based on a job title and location.

    Args:
        title (str): The job title or keywords to search for (e.g., "data scientist").
        location (str, optional): The geographical location to search within. Defaults to "India".
        country (str, optional): The 2-letter country code for Adzuna's API (e.g., "in" for India, "us" for USA). Defaults to "in".

    Returns:
        dict: A dictionary containing job listings under the "results" key.
              Returns {"results": []} if the request fails or no jobs are found."""

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
