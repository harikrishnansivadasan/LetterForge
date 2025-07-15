import streamlit as st
import plotly.express as px
import pandas as pd
import urllib.parse
import json
import ast
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

    st.session_state.cv_skills = [s.lower() for s in cv_data.get("skills", [])]
    st.session_state.jd_skills = [s.lower() for s in jd_data.get("skills", [])]
except Exception as e:
    st.error(f"❌ Failed to load skills from query params: {e}")
    st.stop()


# --- Prompt for LLM Skill Matching ---
def build_skill_analysis_prompt(cv_skills, jd_skills):
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
strictly return valid JSON fromat only. Do not explain anything.
"""


# --- LLM Setup ---
llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct", max_tokens=2000, temperature=0.2
)


def analyze_with_llm(cv_skills, jd_skills):
    prompt = build_skill_analysis_prompt(cv_skills, jd_skills)
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        # Strip code block formatting if present
        if content.startswith("```") and content.endswith("```"):
            content = re.sub(r"^```[a-z]*\n?", "", content)  # remove opening ```
            content = content.rstrip("`").strip()
        return json.loads(content)
    except Exception as e:
        logger.error("⚠️ LLM failed to analyze skills.")
        return None


# --- Analyze with LLM ---
logger.info("🧠 Using AI to analyze your resume against the job description...")
result = analyze_with_llm(cv_data, jd_data)

# if result.startswith("```") and result.endswith("```"):
#     result = result.strip("```").strip()

# result = ast.literal_eval(result)

st.markdown(type(result))

if not result:
    st.error("❌ Failed to analyze skills. Please try again later.")
    st.stop()

# --- Unpack Results ---
matched_skills = result.get("matched_skills", [])
missing_skills = result.get("missing_skills", [])
extra_skills = result.get("extra_skills", [])
match_pct = result.get("match_percentage", 0)
recommended_skills = result.get("recommended_skills", [])
Book_suggestions = result.get("Book_suggestions", [])

print(matched_skills)

# --- Metric Display ---
col1, col2 = st.columns(2)
col1.metric("✅ Matching Skills", len(matched_skills))
col2.metric("📈 Match %", f"{match_pct:.1f}%")

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
                "Count": [len(jd_data), len(matched_skills)],
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

# --- Table View ---
st.subheader("🔍 Skill Matching Breakdown")

table_data = []
for skill in matched_skills:
    table_data.append(
        {"Skill (JD)": skill, "Skill (CV)": skill, "Match Type": "Matched"}
    )
for skill in missing_skills:
    table_data.append(
        {"Skill (JD)": skill, "Skill (CV)": "—", "Match Type": "Missing in CV"}
    )
for skill in extra_skills:
    table_data.append(
        {"Skill (JD)": "—", "Skill (CV)": skill, "Match Type": "Extra in CV"}
    )

df = pd.DataFrame(table_data)
st.dataframe(df, hide_index=True, height=400)

# --- Recommended Skills ---
if recommended_skills:
    st.subheader("✨ Additional Recommended Skills")
    st.markdown(", ".join(recommended_skills))

# --- Course Suggestions ---
if Book_suggestions:
    st.subheader("📚 Book Suggestions")
    for course in Book_suggestions:
        st.markdown(f"- **{course['skill']}**: [{course['Book']}]({course['Author']})")
