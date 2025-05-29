import http.client
from dotenv import load_dotenv
import json
import os

load_dotenv()

# RapidAPI key
rapidapi_key = os.getenv("x-rapidapi-key")

def fetch_job(job_title,location):
    """Fetch job details from RapidAPI"""
    conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")

    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "linkedin-job-search-api.p.rapidapi.com",
    }

    conn.request(
        "GET",
        "/active-jb-7d?limit=10&offset=0&title_filter=%22Data%20Analyst%22&location_filter=%22India%22%20OR%20%22United%20Kingdom%22",
        headers=headers,
    )

    res = conn.getresponse()
    data = res.read()

    final = data.decode("utf-8")
