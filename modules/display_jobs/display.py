"""
===============================================================================
Development History:
-------------------------------------------------------------------------------
Date        | Author           | Change Description
------------|------------------|----------------------------------------------
2025-06-24  | Harikrishnan S   | Initial implementation of display_similar_jobs functions.
2025-07-24  | Harikrishnan S   | Added doc string for display_similar_jobs fn.
            |                  | Added dev history

===============================================================================
"""

import streamlit as st
import pandas as pd


def display_similar_jobs(jobs_raw: str):
    """
    Parses and displays a list of similar jobs using Streamlit UI components.

    This function:
    - Takes a raw string containing job listings separated by double newlines.
    - Each job is expected to follow the format: "Job Title at Company (Location) → URL".
    - Extracts job title, company name, location, and application URL.
    - Displays each job as a row in a formatted Streamlit layout with an "Apply" button.

    If parsing fails for a job entry, default values "Unknown" are used for company and location.

    Args:
        jobs_raw (str): Raw string of job listings fetched from an external source/tool.
                        Example:
                        "ML Engineer at ABC Corp (Bangalore) → https://example.com/job1\n\n
                         Data Scientist at XYZ Inc (Pune) → https://example.com/job2"

    Returns:
        None. Displays the formatted jobs directly in the Streamlit app.
    """

    jobs_text = jobs_raw.strip().split("\n\n")
    job_data = []

    for job in jobs_text:
        parts = job.split(" → ")
        job_info = parts[0].strip()
        job_link = parts[1].strip() if len(parts) == 2 else ""

        try:
            title_part, location_part = job_info.split(" at ")
            company_part, location = location_part.rsplit("(", 1)
            company = company_part.strip()
            location = location.strip(")")
        except:
            title_part = job_info
            company = "Unknown"
            location = "Unknown"

        job_data.append(
            {
                "Job Title": title_part,
                "Company": company,
                "Location": location,
                "Apply URL": job_link,
            }
        )

    st.markdown("### 🧠 Similar Jobs")

    for i, job in enumerate(job_data, start=1):
        col1, col2, col3, col4, col5 = st.columns([0.5, 3, 2, 2, 1])

        with col1:
            st.write(f"**{i}**")
        with col2:
            st.write(job["Job Title"])
        with col3:
            st.write(job["Company"])
        with col4:
            st.write(job["Location"])
        with col5:
            if job["Apply URL"] != "":
                st.markdown(
                    f"""<a href="{job['Apply URL']}" target="_blank">
                                <button style="padding:4px 10px;border:none;border-radius:4px;
                                background-color:#4CAF50;color:white;cursor:pointer;">
                                Apply</button></a>""",
                    unsafe_allow_html=True,
                )
            else:
                st.write("N/A")

        st.markdown("---")
