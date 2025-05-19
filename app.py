import streamlit as st
from modules.fileloader import pdf_loader
from modules.fileloader import text_loader
from modules.ner.ner_capture import parse_resume

st.title("LetterForge")
st.subheader("Create a Perfect cover letter for your job application")

resume = st.sidebar.file_uploader(
    "Upload your resume", type=["pdf", "docx"], key="resume"
)
job_description = st.text_area("Paste your job description here", height=300)
Generate = st.button("Generate Cover Letter")

if Generate:
    if resume is not None:

        """Load the resume content"""
        with st.spinner("processing.."):
            resume_content = pdf_loader.load_pdf(resume)
            jd_content = text_loader.load_text(job_description)
            st.success("Resume loaded successfully!")
            ## calling the ner_capture function- Api call
            # st.write(parse_resume(resume_content))
            st.write(resume_content)
    else:
        st.error("Please upload a resume file.")
