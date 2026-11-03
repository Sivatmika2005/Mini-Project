"""Top navigation bar component."""
import streamlit as st
from utils import db, auth


def render_navbar(logged_in: bool = None, username: str = ""):
    if logged_in is None:
        logged_in = bool(st.session_state.get("user"))

    user = st.session_state.get("user")
    user_display = username or (auth.format_user_display_name(user["username"]) if user else "My Profile")

    if user and "theme" not in st.session_state:
        settings = db.get_user_settings(user["id"])
        st.session_state.theme = settings.get("theme", "Light")
        st.session_state.language = settings.get("language", "English")

    brand_col, actions_col = st.columns([1.8, 3.2], vertical_alignment="center")

    with brand_col:
        st.markdown(
            "<div class='logo'>🌿 AI <span>Wellness</span></div>",
            unsafe_allow_html=True,
        )

    with actions_col:
        if logged_in and user:
            nav_cols = st.columns([1, 1.1, 1.1, 1.4], vertical_alignment="center")

            with nav_cols[0]:
                if st.button("Home", key="nav_home", use_container_width=True):
                    st.session_state.page = "landing"
                    st.rerun()

            with nav_cols[1]:
                if st.button("Resources", key="nav_resources", use_container_width=True):
                    st.session_state.page = "resources"
                    st.rerun()

            with nav_cols[2]:
                if st.button("Dashboard", key="nav_dashboard", use_container_width=True):
                    st.session_state.page = "dashboard"
                    st.rerun()

            with nav_cols[3]:
                with st.popover(f"👤 {user_display} ▼", use_container_width=True):
                    st.markdown(f"<div style='font-weight:700;margin-bottom:4px;color:#1a1a2e;'>{user_display}</div>", unsafe_allow_html=True)
                    st.markdown("<div class='aw-muted' style='font-size:0.82rem;margin-bottom:8px;'>Signed in</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin:6px 0;border-color:rgba(124,124,235,0.15);' />", unsafe_allow_html=True)

                    if st.button("👤 My Profile", key="pop_profile", use_container_width=True):
                        st.session_state.page = "profile"
                        st.rerun()

                    if st.button("✏️ Edit Name", key="pop_edit_name", use_container_width=True):
                        st.session_state.page = "profile"
                        st.rerun()

                    theme_label = "🌙 Dark Theme" if st.session_state.get("theme") == "Light" else "☀️ Light Theme"
                    if st.button(f"🎨 {theme_label}", key="pop_theme", use_container_width=True):
                        new_theme = "Dark" if st.session_state.get("theme") == "Light" else "Light"
                        st.session_state.theme = new_theme
                        db.save_user_settings(user["id"], theme=new_theme)
                        st.rerun()

                    if st.button(f"🌐 Language ({st.session_state.get('language', 'English')})", key="pop_lang", use_container_width=True):
                        st.session_state.page = "profile"
                        st.rerun()

                    st.markdown("<hr style='margin:8px 0;border-color:rgba(124,124,235,0.15);' />", unsafe_allow_html=True)

                    if st.button("🚪 Log Out", key="pop_logout", type="primary", use_container_width=True):
                        auth.logout_user()

        else:
            nav_cols = st.columns([1, 1.1, 1.1], vertical_alignment="center")

            with nav_cols[0]:
                if st.button("Home", key="nav_home", use_container_width=True):
                    st.session_state.page = "landing"
                    st.rerun()

            with nav_cols[1]:
                if st.button("Resources", key="nav_resources", use_container_width=True):
                    st.session_state.page = "resources"
                    st.rerun()

            with nav_cols[2]:
                if st.button("Log In", key="nav_login", type="secondary", use_container_width=True):
                    st.session_state.page = "login"
                    st.rerun()

