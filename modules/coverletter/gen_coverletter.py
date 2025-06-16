import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from modules.logging.logger import logger

load_dotenv()


"""Initialize the LLM"""
# https://groq.com/
llm = ChatGroq(model="llama-3.3-70b-versatile", max_tokens=2000, temperature=0.2)

# Define cover letter prompt template
cover_letter_prompt_template = """
You are an expert assistant tasked with generating a professional and compelling cover letter.

Use the provided entities extracted from the candidate's resume and the job description to write a tailored cover letter. 

Use only relevant information from the resume and that matches the job description to create a concise and impactful letter that highlights the candidate's qualifications and aligns with the job requirements.

Your goals:
- Highlight the candidate's qualifications and relevant experiences.
- Align their skills and achievements with the job role.
- Maintain a formal, confident, and enthusiastic tone.
- Keep the letter concise (around 3 to 5 paragraphs).

Entities from Resume:
{resume_entities}

Entities from Job Description:
{job_description_entities}

Now write the cover letter using these details.
"""


def generate_cover_letter(resume_entities, job_description_entities):
    """
    Generate a cover letter using the provided resume and job description entities.

    Args:
        resume_entities (dict): Parsed entities from the resume.
        job_description_entities (dict): Parsed entities from the job description.

    Returns:
        str: Generated cover letter.
    """
    try:
        # Prepare the prompt for the LLM
        prompt = cover_letter_prompt_template.format(
            resume_entities=json.dumps(resume_entities, indent=2),
            job_description_entities=json.dumps(job_description_entities, indent=2),
        )

        response = llm.invoke(prompt)
        cover_letter = response.content.strip()
        return cover_letter
    except Exception as e:
        logger.error(f"Error loading PDF: {e}")
        return f"Error generating cover letter: {e}"
