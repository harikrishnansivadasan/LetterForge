import http.client
from dotenv import load_dotenv
import json
import os
import urllib.parse


load_dotenv()

# RapidAPI key
rapidapi_key = os.getenv("x-rapidapi-key")


def fetch_job(job_title: str, location: str) -> json:
    """Fetch job details from RapidAPI"""
    conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")

    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "linkedin-job-search-api.p.rapidapi.com",
    }
    # Encode the job title and location for URL
    job_title_encoded = urllib.parse.quote(job_title)
    location_encoded = urllib.parse.quote(location)

    # Construct the URL with encoded parameters
    # Example: Fetching jobs for "Data Analyst" in "India" or "United Kingdom"
    conn.request(
        "GET",
        "/active-jb-7d?limit=10&offset=0&title_filter=%22{job_title_encoded}%22&location_filter=%22{location_encoded}%22",
        headers=headers,
    )

    res = conn.getresponse()
    data = res.read()

    final = data.decode("utf-8")
    