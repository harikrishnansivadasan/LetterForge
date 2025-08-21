# ✉️ LetterForge

**LetterForge** is an AI-powered web app that helps job seekers generate customized cover letters, analyze CV vs job descriptions, and discover relevant job listings — all in one place.

Built with 🐍 Python, ⚡ Streamlit, and 🤖 LLMs, LetterForge streamlines your job application process with smart automation.

---

## 🚀 Features

- 🔍 **CV vs JD Analyzer**: Extracts and compares key skills between your resume and job description.
- ✉️ **Cover Letter Generator**: Crafts tailored, professional letters using your resume and job target.
- 🧠 **Skill Gap Suggestions**: Highlights missing skills and suggests improvements or courses.
- 💼 **Live Job Finder**: Fetches matching job listings using external APIs (Adzuna, RapidAPI).
- 📊 **Match Score**: Calculates how well your profile fits the job description.

---

## 🧱 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **AI/LLM**: OpenAI / Groq via LangChain
- **Job APIs**: Adzuna, RapidAPI
- **Deployment**: Docker, AWS EC2, GitHub Actions CI/CD

---

## 🛠️ Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/LetterForge.git
   cd LetterForge
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
3. **Add your .env file**
   create .env file in root folder and add your api keys
   ```bash
    GROQ_API_KEY=your_key
    RAPIDAPI_KEY=your_key
    ADZUNA_APP_ID=your_id
    ADZUNA_APP_KEY=your_key
5. **Run the app**
   ```bash
   streamlit run app.py
