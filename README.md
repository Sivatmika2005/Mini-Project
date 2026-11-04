# 🌿 AI Mental Wellness Companion

An intelligent, full-stack mental wellness platform powered by **React**, **FastAPI**, **Firebase Cloud Firestore**, and **Machine Learning Emotion Intelligence**.

---

## 🏗️ Architecture

- **Frontend**: **React 18** + **Vite** (`frontend/`) running on `http://localhost:5173`
- **Backend**: **FastAPI** + **Uvicorn** (`server.py`) running on `http://localhost:8001`
- **Database & Auth**: **Firebase Authentication** + **Cloud Firestore**
- **Machine Learning**: Scikit-Learn Emotion Classifier, Web Audio API pitch autocorrelation, Computer Vision face landmark tracking, and MedGemma conversational engine.

---

## ✨ Key Features

1. **🏠 Interactive Dashboard**:
   - Real-time wellness KPIs: Wellness Score, Stress Index, Daily Check-In Streak, and Journal count.
   - **AI Robot Wellness Companion**: Interactive voice and text conversation with speech recognition and browser speech synthesis.
   - **📷 Vision & Voice Emotion AI**: Live biometric analysis detecting emotion via camera facial expression cues and vocal modulation (pitch $F_0$ & tone intensity) with instant interventions (Box Breathing, 5-4-3-2-1 Grounding, Compassion, Rest, and Positive reinforcement).
2. **📝 Daily Check-In**:
   - Track mood, stress (1–10), energy (1–10), sleep quality, and daily notes with one-click syncing from Vision & Voice AI.
3. **💬 AI Therapy Chat**:
   - Conversational mental wellness support powered by **External AI API** (Google Gemini / OpenAI / Groq) with multi-turn conversation memory, emotional background awareness, and crisis safety protocol.
4. **📔 Personal Journal**:
   - Secure personal reflections diary with categorized tagging and history tracking.
5. **🌱 Guided Wellness Exercises**:
   - Interactive 4-4-4-4 Box Breathing, sensory grounding, and guided mindfulness practices.
6. **🔎 Insights & Encrypted Clinician Report Generator**:
   - Historical mood trends and distribution charts.
   - 1-click **HIPAA/Clinical Summary Report** export with Web Crypto AES-GCM-256 encrypted backup for therapy sessions.
7. **☎️ Crisis Helplines & 🩺 Professional Support**:
   - 24/7 verified crisis resources, helplines, and directory of licensed psychiatric support.
8. **⚙️ Profile & Customization**:
   - Multi-theme switching (Default, Soft Pastel, Ocean Breeze) and English/Tamil language localization.

---

## 🚀 Quick Start Guide (Windows)

### Double-Click Launcher
Double-click `start_app.bat` (or `start.bat`) to launch both servers and open your browser automatically:
```cmd
start_app.bat
```

### Manual Command Line Launch

#### 1. Start Python FastAPI Backend
```powershell
# Activate Python 3.12 virtual environment
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Run backend API
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### 2. Start React Frontend
```powershell
cd frontend
npm install
npm run dev
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Canvas-Confetti, Web Audio API, Web Speech API, CSS3 |
| **Backend API** | Python 3.12, FastAPI, Uvicorn, Starlette, Pydantic |
| **Auth & Cloud** | Firebase Admin SDK, Firebase Web Auth, Cloud Firestore |
| **Machine Learning** | Scikit-Learn, Joblib, NumPy, Pandas, Matplotlib, Seaborn |
| **Security** | Web Crypto API (AES-GCM-256), Salted hashing, CORS isolation |
