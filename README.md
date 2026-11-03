# 🌿 AI Mental Wellness Companion

An intelligent, interactive mental wellness application powered by **Machine Learning Emotion Intelligence** and **Streamlit**.

---

## ✨ Key Features

- **💬 ChatGPT-Style Interactive 2-Way Chat**: Talk through emotions, daily reflections, stress management, and grounding exercises with real-time ML emotion detection.
- **📝 Daily Check-In**: Quick emotional tracking for mood, stress, energy levels, and sleep quality.
- **📈 Mood Tracker & Analytics**: Dynamic trend visualizations and historical mood distribution charts.
- **📔 Personal Journal**: Private space to log reflections, thoughts, and personal growth.
- **🌱 Interactive Wellness Tips**: Box breathing exercises, 5-4-3-2-1 grounding techniques, and mindfulness practices.
- **🔎 Progress Insights**: Non-diagnostic mood trend summaries and personalized well-being suggestions.
- **🔒 Privacy First**: Local storage with salted password hashing and secure session management.

---

## 🚀 Quick Start Guide

### Windows Quick Launch
Double-click `start.bat` to automatically set up the Python 3.12 environment and launch the app:
```cmd
start.bat
```

### Manual Command Line Setup (Python 3.12)
1. **Create & Activate Virtual Environment**:
   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```powershell
   streamlit run app.py
   ```

---

## 🛠️ Technology Stack

- **Frontend / UI**: Streamlit
- **Backend & Logic**: Python 3.12
- **ML & Analytics**: Scikit-Learn, Joblib, Pandas, NumPy, Matplotlib, Seaborn
- **Database**: SQLite3
- **LLM Integration**: Support for Gemini, Anthropic, OpenAI, Groq & Local ML Emotion Fallback Engine
