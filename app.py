import streamlit as st
from modules.fileloader import pdfloader

st.title("LetterForge")
st.subheader("Create a Perfect cover letter for your job application")

resume = st.sidebar.file_uploader(
    "Upload your resume", type=["pdf", "docx"], key="resume"
)
job_description = st.text_area("Paste your job description here", height=300)
Generate = st.button("Generate Cover Letter")

if Generate:
    if resume is not None:
        with st.spinner("processing.."):
            resume_content = pdfloader.load_pdf(resume)
            st.success("Resume loaded successfully!")
            st.write(resume_content)
    else:
        st.error("Please upload a resume file.")
