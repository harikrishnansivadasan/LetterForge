import logging
from langchain.agents import Tool, initialize_agent
from langchain_groq import ChatGroq
from langchain.agents.agent_types import AgentType
from modules.jobfetch.jobs import fetch_job  # Import the fetch_job function
from modules.jobfetch.jobs_adzuna import fetch_jobs_adzuna  # Import the Adzuna function
from modules.logging.logger import logger
from langchain.tools import tool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


# class JobSearchInput(BaseModel):
#     job_title: str = Field(..., description="Job title to search for")
#     location: str = Field(..., description="Location to search in")


# LangChain-compatible wrapper
@tool("RapidJobSearch", return_direct=True)
def job_search_tool_func(query: str) -> str:
    """
    Search for recent job listings based on a job title and location.

    This tool fetches job openings using external job APIs based on user queries
    in the format: "<Job Title> in <Location>" (e.g., "ML Engineer in India").

    Parameters
    ----------
    query : str
        A natural language string specifying the job role and location,
        formatted as "<Job Title> in <Location>".

    Returns
    -------
    str
        A formatted string containing a list of job results including title,
        company, location, and a URL to the job posting.
    """
    try:
        logger.info(f"[TOOL] Tool called with query: {query}")

        parts = query.split(" in ")
        if len(parts) != 2:
            logger.warning("[TOOL] Invalid query format")
            return "⚠️ Please provide input in the format: 'Job Title in Location'."

        job_title = parts[0].strip() or "Software Engineer"
        location = parts[1].strip() or "India"

        logger.info(f"[TOOL] Parsed as title={job_title}, location={location}")
        # jobs = fetch_job(job_title, location)         # Use this for Rapid API function

        jobs = fetch_jobs_adzuna(
            job_title, location
        )  # Use this for Adzuna Api function

        jobs = jobs.get("results", [])  # Extract the list of jobs from the response
        logger.info(f"[TOOL] Jobs fetched: {len(jobs)} jobs returned")

        # print(f"Jobs fetched: {jobs}")
        # print(f"Type of jobs: {type(jobs)}")

        if not jobs:
            return "🔍 No jobs found."

        # RapidAPI returns a different structure
        # output = "\n\n".join(
        #     f"{j.get('job_title')} at {j.get('company_name')} ({j.get('location')}) → {j.get('job_url')}"
        #     for j in jobs
        # )

        # Adzuna API returns a different structure
        output = "\n\n".join(
            f"{j.get('title')} at {j.get('company', {}).get('display_name')} "
            f"({j.get('location', {}).get('display_name')}) → {j.get('redirect_url')}"
            for j in jobs
        )

        logger.info(f"[TOOL] Returning {len(jobs)} job(s)")
        return output

    except Exception as e:
        logger.error("[TOOL] Exception occurred" + str(e))
        return "❌ An error occurred while fetching jobs."


# Define the LangChain Tool
# job_tool = job_search_tool_func

# Agent setup
groq_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
llm_tools = groq_llm.bind_tools([job_search_tool_func])


def run_job_agent_from_description(jd_text: str) -> str:
    try:
        agent = initialize_agent(
            tools=[job_search_tool_func],
            llm=llm_tools,
            agent_type=AgentType.OPENAI_MULTI_FUNCTIONS,
            verbose=True,
            handle_parsing_errors=True,
        )

        prompt = f"""
You are a job assistant.

Instructions:
1. Extract job title and location from the job description below.
2. If no location, use "India". If no title, use "Software Engineer".
3. Use the function called 'RapidJobSearch' with input in the format: "Job Title in Location".
4. ONLY use the tool to answer. Do not respond otherwise.

Job Description:
            {jd_text}
        """
        result = agent.run({prompt})
        return result

    except Exception as e:
        logger.exception("Agent execution failed." + str(e))
        return "Agent failed to run."
