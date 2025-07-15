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
    Fetch real-time job listings only when the user is explicitly looking
    for job openings, using phrases like 'find jobs', 'search openings',
    or 'show me positions'. Input must follow the format: '<Job Title> in <Location>'

    warning : Do NOT use this tool to answer questions about career advice, skills, salaries, or general information.

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
def common_llm():
    groq_llm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.2
    )
    llm_tools = groq_llm.bind_tools([job_search_tool_func])
    agent = initialize_agent(
        tools=[job_search_tool_func],
        llm=llm_tools,
        agent_type=AgentType.OPENAI_MULTI_FUNCTIONS,
        verbose=True,
        handle_parsing_errors=True,
    )
    return agent


def run_user_query_or_job_search(jd_text: str) -> str:
    try:
        agent = common_llm()

        prompt = f"""
    You are a smart job assistant.

    Instructions:
    1. Read the job description provided.
    2. Extract a suitable job title and location based on the content.
    3. If location is missing, default to "India". If title is missing, default to "Software Engineer".
    4. Create a query in the format: "Job Title in Location" (e.g., "ML Engineer in Kochi").
    5. Use the tool 'RapidJobSearch' with the query to fetch jobs.
    6. ONLY respond using the tool. Do NOT answer directly.

    

    Job Description:
            {jd_text}
        """
        try:
            logger.info("Running agent to fetch jobs using prompt: ")
            result = agent.run(prompt)
            return result.content.strip() if hasattr(result, "content") else str(result)
        except Exception as e:
            logger.error("Error running agent: " + str(e))
            return "Agent failed to run due to an error."

    except Exception as e:
        logger.exception("Agent execution failed." + str(e))
        return "Agent failed to run."
