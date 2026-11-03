"""AI Mental Wellness Companion - Main Streamlit Application Entrypoint."""
import os
import sys

# Load environment variables from .env early so `FIREBASE_WEB_API_KEY` is available
from dotenv import load_dotenv
load_dotenv()

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils import auth, db, styles

# 1. Configure Streamlit Page
st.set_page_config(
    page_title="AI Mental Wellness Companion",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 3. Initialize SQLite Database Schema
db.init_db()

# 4. Restore User Session on Startup/Refresh
auth.restore_session_on_startup()

# Load user settings if logged in
user = st.session_state.get("user")
if user and "theme" not in st.session_state:
    settings = db.get_user_settings(user["id"])
    st.session_state.theme = settings.get("theme", "Light")
    st.session_state.language = settings.get("language", "English")

# 2. Inject Custom Aesthetic CSS with selected theme
styles.inject_base_css(st)

# 5. Initialize Navigation Session State
if "page" not in st.session_state:
    st.session_state.page = "landing"

# 6. Route to Target Page Module
current_page = st.session_state.page

if current_page == "landing":
    from pages_content import landing
    landing.render()
elif current_page == "login":
    from pages_content import login
    login.render()
elif current_page == "dashboard":
    from pages_content import dashboard
    dashboard.render()
elif current_page == "checkin":
    from pages_content import checkin
    checkin.render()
elif current_page == "chat":
    from pages_content import chat
    chat.render()
elif current_page == "journal":
    from pages_content import journal
    journal.render()
elif current_page == "wellness_tips":
    from pages_content import wellness_tips
    wellness_tips.render()
elif current_page == "insights":
    from pages_content import insights
    insights.render()
elif current_page == "resources":
    from pages_content import resources
    resources.render()
elif current_page == "professional_support":
    from pages_content import professional_support
    professional_support.render()
elif current_page == "profile":
    from pages_content import profile
    profile.render()
else:
    from pages_content import landing
    landing.render()
