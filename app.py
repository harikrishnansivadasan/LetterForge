import streamlit as st
from modules.fileloader import pdf_loader
from modules.fileloader import text_loader
from modules.ner.ner_capture import parse_resume, parse_jd
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from modules.logging.logger import logger
from modules.coverletter.gen_coverletter import generate_cover_letter
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from modules.jobfetch.agent import run_job_agent_from_description

# Load environment variables
load_dotenv()

st.title("LetterForge")
st.subheader("Create a Perfect cover letter for your job application")

resume = st.sidebar.file_uploader(
    "Upload your resume", type=["pdf", "docx"], key="resume"
)
job_description = st.text_area("Paste your job description here", height=300)
Generate = st.button("Generate Cover Letter")
Find = st.button("🔍 Find Jobs ")

# Initialize the LLM
# https://groq.com/
llm = ChatGroq(model="llama-3.3-70b-versatile", max_tokens=2000, temperature=0.2)

# Initialize a status box to show processing status
staus_box = st.empty()

# Store parsed data
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
    logger.info("-------------------Generate button clicked--------------------")
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
                    logger.info("Cover letter generated successfully!")
                    st.session_state.cover_letter = (
                        cover_letter  # Store generated cover letter
                    )

                except Exception as gen_error:
                    logger.error(f"Error generating cover letter: {gen_error}")
                    staus_box.error(f"Error generating cover letter: {gen_error}")

                # Display the generated cover letter in a text area
                if "cover_letter" in st.session_state:
                    st.text_area(
                        "Generated Cover Letter",
                        value=cover_letter,
                        height=700,
                        key="cover_letter_output",
                    )
                    # Download button for the cover letter
                    download_clicked = st.download_button(
                        label="Download Cover Letter",
                        data=st.session_state.cover_letter,
                        file_name="cover_letter.txt",
                        mime="text/plain",
                        key="download_cover_letter",
                    )
                    if download_clicked:
                        logger.info("Cover letter download started.")

            except Exception as e:
                logger.error(f"Error loading PDF: {e}")
                staus_box.error(e)

    else:
        staus_box.error("Please upload Resume and Jd.")

# Job Search Functionality
if Find:
    logger.info("-------------------Find Jobs button clicked--------------------")
    if job_description:
        with st.spinner("Searching..."):
            result = run_job_agent_from_description(job_description)
            st.session_state.similar_jobs = result
            staus_box.success("Done.")
    else:
        staus_box.warning("Please paste a job description.")

# Display similar jobs if available
if "similar_jobs" in st.session_state:
    st.markdown("### 🧠 Jobs Found by AI")
    st.markdown(st.session_state.similar_jobs)


# Chat Interface
if 1 == 1:  # st.session_state.cover_letter is not None:
    st.sidebar.title("Chat Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.sidebar.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input for chat
    user_input = st.sidebar.chat_input("Ask anything...", key="user_input")

    if user_input:
        # Add user ip to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        try:
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You're an assistant helping a candidate improve their job application. Use the resume and job description entities to help and answer questions.",
                    ),
                    (
                        "user",
                        """ Resume: {resume_entities}
                     Jd: {job_description_entities}
                     User Question: {user_input}""",
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                ]
            )
            # converting history to Langchain messages
            # This is necessary to format the chat history correctly for the LLM
            formatted_history = []
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    formatted_history.append(HumanMessage(content=message["content"]))
                elif message["role"] == "assistant":
                    formatted_history.append(AIMessage(content=message["content"]))

            # Format the prompt with the user's input and chat history
            # This is where we prepare the prompt for the LLM
            formatted_prompt = prompt.format_messages(
                resume_entities=st.session_state.resume_entities,
                job_description_entities=st.session_state.jd_entities,
                chat_history=formatted_history,
                user_input=user_input,
            )
            response = llm.invoke(formatted_prompt)
            bot_reply = response.content.strip()

        except Exception as e:
            logger.error(f"Error formatting prompt: {e}")
            bot_reply = "Sorry, I couldn't process your request. Please try again."

        # Adding response to chat history
        st.session_state.chat_history.append(
            {"role": "assistant", "content": bot_reply}
        )
        # Display the bot's reply in the chat interface
        st.rerun()
