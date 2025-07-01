import http.client
from dotenv import load_dotenv
import json
import os
import urllib.parse
from modules.logging.logger import logger

load_dotenv()

# RapidAPI key
rapidapi_key = os.getenv("x-rapidapi-key")

# Dummy data for testing
dummy = [
    {
        "job_title": "Backend Engineer",
        "company_name": "TechCorp",
        "location": "location",
        "job_url": "https://example.com/job/1",
    },
    {
        "job_title": "Senior Backend Developer",
        "company_name": "InnoSoft",
        "location": "location",
        "job_url": "https://example.com/job/2",
    },
]


def fetch_job(job_title: str, location: str) -> json:
    try:
        # RapidAPI key
        rapidapi_key = os.getenv("x-rapidapi-key")

        """Fetch job details from RapidAPI"""
        conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")

        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "linkedin-job-search-api.p.rapidapi.com",
        }
        # Encode the job title and location for URL
        job_title_encoded = urllib.parse.quote(job_title)
        location_encoded = urllib.parse.quote(location)
        # endpoint = f"/active-jb-7d?limit=10&offset=0&title_filter=%22{job_title_encoded}%22&location_filter=%22{location_encoded}%22"
        # Construct the URL with encoded parameters
        # Example: Fetching jobs for "Data Analyst" in "India" or "United Kingdom"
        conn.request(
            "GET",
            f"/active-jb-7d?limit=10&offset=0&title_filter=%22{job_title_encoded}%22&location_filter=%22{location_encoded}%22",
            headers=headers,
        )

        res = conn.getresponse()
        data = res.read()

        final = data.decode("utf-8")
        return final.loads()  # Convert JSON string to Python object

        # return dummy  # For testing, return dummy data
    except Exception as e:
        logger.error("Failed to fetch jobs from RapidAPI.")
        return dummy
