import streamlit as st
from modules.fileloader import pdf_loader
from modules.fileloader import text_loader
from modules.ner.ner_capture import parse_resume, parse_jd
from modules.logging.logger import logger
from modules.coverletter.gen_coverletter import generate_cover_letter

st.title("LetterForge")
st.subheader("Create a Perfect cover letter for your job application")

resume = st.sidebar.file_uploader(
    "Upload your resume", type=["pdf", "docx"], key="resume"
)
job_description = st.text_area("Paste your job description here", height=300)
Generate = st.button("Generate Cover Letter")

# Initialize a status box to show processing status
staus_box = st.empty()

""" Store parsed data """
# Initialize session state variables to store parsed resume entities
if "resume_entities" not in st.session_state:
    st.session_state.resume_entities = None

# Initialize session state variables to store parsed job description entities
if "jd_entities" not in st.session_state:
    st.session_state.jd_entities = None

# Initialize session state variable to store cover letter
if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = None

if Generate:
    # check if both resume and job description are provided
    if resume is not None and job_description is not None and len(job_description) > 0:
        with st.spinner("processing.."):
            try:
                # loading the resume and job description files
                # Load Resume and Job Description
                resume_content = pdf_loader.load_pdf(resume)
                jd_content = text_loader.load_text(job_description)
                staus_box.success("Files loaded successfully!")
                logger.info("Files loaded successfully!")

                # calling the ner_capture function- Api call
                # Parse Resume and Job Description
                try:
                    resume_entities = parse_resume(resume_content)
                    jd_entities = parse_jd(jd_content)
                    st.session_state.resume_entities = (
                        resume_entities  # Store parsed resume entities
                    )
                    st.session_state.jd_entities = (
                        jd_entities  # Store parsed job description entities
                    )
                    staus_box.success("Entities extracted successfully!")
                    logger.info("Entities extracted successfully!")
                except Exception as parse_error:
                    logger.error(f"Error parsing files: {parse_error}")
                    st.error(f"Error parsing files: {parse_error}")

                # calling the gen_coverletter function- Api call
                # Generate Cover Letter
                try:
                    cover_letter = generate_cover_letter(resume_entities, jd_entities)
                    staus_box.success("Cover letter generated successfully!")
                    st.session_state.cover_letter = (
                        cover_letter  # Store generated cover letter
                    )
                    # Display the generated cover letter in a text area
                    st.text_area(
                        "Generated Cover Letter",
                        value=cover_letter,
                        height=700,
                        key="cover_letter_output",
                    )
                    # Download button for the cover letter
                    if st.session_state.cover_letter:
                        st.download_button(
                            label="Download Cover Letter",
                            data=st.session_state.cover_letter,
                            file_name="cover_letter.txt",
                            mime="text/plain",
                            key="download_cover_letter",
                        )

                    logger.info("Cover letter generated successfully!")

                except Exception as gen_error:
                    logger.error(f"Error generating cover letter: {gen_error}")
                    staus_box.error(f"Error generating cover letter: {gen_error}")

            except Exception as e:
                logger.error(f"Error loading PDF: {e}")
                staus_box.error(e)

    else:
        staus_box.error("Please upload Resume and Jd.")


""" Chat Interface """
