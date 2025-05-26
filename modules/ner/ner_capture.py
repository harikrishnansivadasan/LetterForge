import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

"""Initialize the LLM"""
llm = ChatGroq(model="llama-3.3-70b-versatile", max_tokens=2000, temperature=0.2)

# Define resume prompt template
resume_prompt_template = """
You are tasked with parsing a resume. Your objective is to extract relevant information in a valid structured 'JSON' format. Do not write explanations or any other preambles, do not add or write anything out of context, use only the given information.

**Task:** Extract key information from the following resume text, especially Skills, Experience, Education.

**Resume Text:**
{text}

**Instructions:**
Please extract the following information and format it in a clear structure as below. Assure to maintain these fields intact (do not change the case to lower):

1. **Contact Information:**
- Name:        

2. **Education:**
- Institution Name:
- Degree:
- Field of Study:
- Graduation Date:

3. **Experience:**
- Job Title:        
- Responsibilities/Projects:

4. **Projects:**
- Project Title:
- Description/Technologies Used:
- Outcomes/Results:

5. **Skills:**
- Programming Languages:
- Technologies/Tools/frameworks:

6. **Additional Information:** (if applicable)
- Certifications:
- Awards or Honors:
- Professional Affiliations:       

strictly return in json dictionary format 
"""

# Define job description prompt template
jd_prompt_template = """
You are tasked with parsing a job description. Your objective is to extract relevant information in a valid structured 'JSON' format. Do not write explanations or any other preambles, do not add or write anything out of context, use only the given information.
**Task:** Extract key information from the following job description text, especially Skills, Experience, Education.
**Job Description Text:**   
{text}
**Instructions:**
Please extract the following information and format it in a clear structure as below. Assure to maintain these fields intact (do not change the case to lower):
1. **Job Title:**
- Job Title:
2. **Company Information:**
- Company Name:
- Company Description:
3. **Job Responsibilities:**
- Responsibilities:
4. **Required Qualifications:**
- Required Skills:
5. **Preferred Qualifications:**
- Preferred Skills:
6. **Location:**
- Job Location:
strictly return in json dictionary format 
"""

# Create the prompt object once
resume_prompt = ChatPromptTemplate.from_template(resume_prompt_template)
jd_prompt = ChatPromptTemplate.from_template(jd_prompt_template)

# Function to parse resume and return structured JSON data
def parse_resume(text: str) -> dict:
    """
    Parse resume and return structured JSON data.

    Args:
        text (str): The job description text to parse.

    Returns:
        dict: A dictionary containing the parsed information.
    """
    formatted_prompt = resume_prompt.format(text=text)
    response = llm.invoke(formatted_prompt)

    # Clean and parse the JSON response
    cleaned = re.sub(r"^```json|```$", "", response.content.strip(), flags=re.MULTILINE)
    parsed_json = json.loads(cleaned)

    return parsed_json

# Function to parse jd and return structured JSON data
def parse_jd(text: str) -> dict:
    """
    Parse a job description and return structured JSON data.
    
    Args:
        text (str): The job description text to parse.
    
    Returns:
        dict: A dictionary containing the parsed information.
    """
    formatted_prompt = jd_prompt.format(text=text)
    response = llm.invoke(formatted_prompt)

    # Clean and parse the JSON response
    cleaned = re.sub(r"^```json|```$", "", response.content.strip(), flags=re.MULTILINE)
    parsed_json = json.loads(cleaned)

    return parsed_json
