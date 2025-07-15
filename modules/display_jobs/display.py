import streamlit as st
import pandas as pd


def display_similar_jobs(jobs_raw: str):
    
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
