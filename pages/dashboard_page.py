"""
===============================================================================
Development History:
-------------------------------------------------------------------------------
Date        | Author           | Change Description
------------|------------------|----------------------------------------------
2025-06-24  | Harikrishnan S   | Initial implementation of dashboard functions.
2025-07-24  | Harikrishnan S   | Added Dev history.


===============================================================================
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import urllib.parse
import json
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from langchain_groq import ChatGroq
from modules.logging.logger import logger

# --- Streamlit Setup ---
st.set_page_config(layout="wide")
st.title("🎯 Skill Analyzer Dashboard")

# --- Load CV/JD skills from query params ---
params = st.query_params
try:
    cv_data = json.loads(urllib.parse.unquote(params.get("cv", "{}")))
    jd_data = json.loads(urllib.parse.unquote(params.get("jd", "{}")))

    print(cv_data, jd_data)

    st.session_state.cv_skills = [s.lower() for s in cv_data.get("skills", [])]
    st.session_state.jd_skills = [s.lower() for s in jd_data.get("skills", [])]
except Exception as e:
    st.error(f"❌ Failed to load skills from query params: {e}")
    st.stop()


# --- Prompt for LLM Skill Matching ---
def build_skill_analysis_prompt(cv_skills, jd_skills):
    """
    Builds a prompt to send to the LLM for analyzing skill overlap between a CV and a job description.

    Parameters:
        cv_skills (list): A list of skills extracted from the candidate's CV.
        jd_skills (list): A list of skills required by the job description.

    Returns:
        str: A formatted prompt string containing both skill lists and a JSON response format
             that instructs the LLM to return matched, missing, and extra skills, as well as
             match percentage, recommended skills, and relevant book suggestions.
    """

    return f"""
        You are an expert resume screener.

        Compare the candidate's CV skills and job description (JD) skills below.

        CV Skills:
        {cv_skills}

        JD Skills:
        {jd_skills}

        Please return your response in the following JSON format:
        {{
        "matched_skills": [...],
        "missing_skills": [...],
        "extra_skills": [...],
        "match_percentage": 0-100,
        "recommended_skills": [...],
        "Book_suggestions": [
            {{ "skill": "...", "Book": "...", "Author": "..." }}
        ]
        }}
        strictly return valid JSON format only. Do not explain anything.
        """


# --- LLM Setup ---
llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct", max_tokens=2000, temperature=0.2
)


def analyze_with_llm(cv_skills, jd_skills):
    """
    Sends a structured prompt to the LLM to analyze and compare CV and JD skills.

    This function builds a prompt using the provided skill lists, invokes the LLM using the `llm` instance,
    and parses the JSON response returned by the model. It extracts matched skills, missing skills, extra
    skills, match percentage, recommended skills, and book suggestions.

    Parameters:
        cv_skills (list): A list of skills from the candidate's CV.
        jd_skills (list): A list of required skills from the job description.

    Returns:
        dict or None: A dictionary containing the analyzed result with keys like:
            - "matched_skills": list of common skills,
            - "missing_skills": list of skills in JD but not in CV,
            - "extra_skills": list of skills in CV but not in JD,
            - "match_percentage": a number from 0–100,
            - "recommended_skills": list of useful additional skills,
            - "Book_suggestions": list of book recommendations in dicts.

        Returns None if the LLM call fails or the response is invalid.
    """

    prompt = build_skill_analysis_prompt(cv_skills, jd_skills)
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        if content.startswith("```") and content.endswith("```"):
            content = re.sub(r"^```[a-z]*\n?", "", content)
            content = content.rstrip("`").strip()
        return json.loads(content)
    except Exception as e:
        logger.error(f"⚠️ LLM failed to analyze skills. {e}")
        return None


# --- Analyze with LLM ---
logger.info("🧠 Using AI to analyze your resume against the job description...")
result = analyze_with_llm(cv_data, jd_data)
print(result)
if not result:
    st.error("❌ Failed to analyze skills. Please try again later.")
    st.stop()

matched_skills = result.get("matched_skills", [])
missing_skills = result.get("missing_skills", [])
extra_skills = result.get("extra_skills", [])
match_pct = result.get("match_percentage", 0)
recommended_skills = result.get("recommended_skills", [])
Book_suggestions = result.get("Book_suggestions", [])

# --- Metric Display ---
col1, col2 = st.columns(2)
col1.metric("✅ Matching Skills", len(matched_skills))
col2.metric("📈 Match %", f"{match_pct:.1f}%")

# --- Match % Gauge ---
gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=match_pct,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Match %"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#00cc96"},
            "steps": [
                {"range": [0, 50], "color": "#ffa39e"},
                {"range": [50, 80], "color": "#ffd666"},
                {"range": [80, 100], "color": "#b7eb8f"},
            ],
        },
    )
)
st.plotly_chart(gauge, use_container_width=True)

# --- Sidebar Filters ---
st.sidebar.header("🔧 Filter Skill Categories")
show_matched = st.sidebar.checkbox("✅ Matched Skills", True)
show_missing = st.sidebar.checkbox("❌ Missing Skills", True)
show_extra = st.sidebar.checkbox("🌀 Extra Skills", True)


# --- Badge function ---
def badge(skill, color="#1890ff"):
    return f'<span style="background-color:{color}; color:white; padding:4px 10px; border-radius:8px; margin:2px; display:inline-block;">{skill}</span>'


# --- Display Skill Tags ---
if show_missing:
    st.markdown("**🧠 Missing Skills**", unsafe_allow_html=True)
    st.markdown(
        " ".join([badge(skill, "#ff4d4f") for skill in missing_skills]),
        unsafe_allow_html=True,
    )

if show_matched:
    st.markdown("**✅ Matched Skills**", unsafe_allow_html=True)
    st.markdown(
        " ".join([badge(skill, "#52c41a") for skill in matched_skills]),
        unsafe_allow_html=True,
    )

if show_extra:
    st.markdown("**🌀 Extra Skills in CV**", unsafe_allow_html=True)
    st.markdown(
        " ".join([badge(skill, "#1890ff") for skill in extra_skills]),
        unsafe_allow_html=True,
    )

# --- Visualize Missing Skills ---
st.subheader("🧠 Missing Skills in CV")
viz_type = st.radio(
    "Options:", ["Word Cloud", "Treemap", "Coverage Bars"], horizontal=True
)

if missing_skills:
    if viz_type == "Word Cloud":
        wordcloud = WordCloud(width=800, height=400).generate(" ".join(missing_skills))
        fig_wc, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig_wc)

    elif viz_type == "Treemap":
        treemap_data = pd.DataFrame(
            {
                "Skill": missing_skills,
                "Importance": [len(s) for s in missing_skills],
                "Parent": "Missing",
            }
        )
        fig = px.treemap(treemap_data, path=["Parent", "Skill"], values="Importance")
        st.plotly_chart(fig, use_container_width=True)

    else:
        coverage_data = pd.DataFrame(
            {
                "Category": ["Required by JD", "Covered by CV"],
                "Count": [len(st.session_state.jd_skills), len(matched_skills)],
            }
        )
        fig = px.bar(
            coverage_data,
            x="Category",
            y="Count",
            color="Category",
            color_discrete_map={
                "Required by JD": "#EF553B",
                "Covered by CV": "#00CC96",
            },
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.success("🎉 No missing skills!")

# --- Table View with Search ---
search_term = st.text_input("🔍 Search Skills")
filtered_table_data = []

if show_matched:
    filtered_table_data += [
        {"Skill (JD)": s, "Skill (CV)": s, "Match Type": "Matched"}
        for s in matched_skills
    ]
if show_missing:
    filtered_table_data += [
        {"Skill (JD)": s, "Skill (CV)": "—", "Match Type": "Missing in CV"}
        for s in missing_skills
    ]
if show_extra:
    filtered_table_data += [
        {"Skill (JD)": "—", "Skill (CV)": s, "Match Type": "Extra in CV"}
        for s in extra_skills
    ]

df_filtered = pd.DataFrame(filtered_table_data)

if search_term:
    df_filtered = df_filtered[
        df_filtered.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)
    ]

st.subheader("🔍 Skill Matching Breakdown")
st.dataframe(df_filtered, hide_index=True, height=400)

# --- Download Report ---
csv_data = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Skill Report", csv_data, "skill_report.csv", "text/csv")

# --- Recommended Skills ---
if recommended_skills:
    st.subheader("✨ Additional Recommended Skills")
    st.markdown(", ".join(recommended_skills))

# --- Book Suggestions ---
if Book_suggestions:
    st.subheader("📚 Book Suggestions")
    for course in Book_suggestions:
        st.markdown(f"- **{course['skill']}**: [{course['Book']}]({course['Author']})")
