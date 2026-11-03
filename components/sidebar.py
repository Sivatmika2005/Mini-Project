"""Sidebar navigation for authenticated app pages."""
import streamlit as st
from utils import auth
from utils.translations import t


def render_sidebar(include_nav=True):
    menu = [
        (t("nav_dashboard"), "dashboard"),
        (t("nav_checkin"), "checkin"),
        (t("nav_chat"), "chat"),
        (t("nav_journal"), "journal"),
        (t("nav_wellness_tips"), "wellness_tips"),
        (t("nav_insights"), "insights"),
        (t("nav_resources"), "resources"),
        (t("nav_professional_support"), "professional_support"),
    ]

    with st.sidebar:
        st.markdown(
            f"<div style='font-family:Poppins,sans-serif;font-weight:800;font-size:1.25rem;"
            f"margin-bottom:4px;color:var(--ink, #1a1a2e);'>{t('app_title')}</div>",
            unsafe_allow_html=True,
        )
        user = st.session_state.get("user")
        if user:
            greeting = auth.get_user_greeting(user.get("username", ""))
            greet_col, set_col = st.columns([3, 1], vertical_alignment="center")
            with greet_col:
                st.markdown(f"<div style='font-weight:600;font-size:0.9rem;color:var(--accent, #7c7ceb);margin-bottom:0;'>{greeting}</div>", unsafe_allow_html=True)
            with set_col:
                if st.button("⚙️", key="side_quick_settings", help=t("nav_profile")):
                    st.session_state.page = "profile"
                    st.rerun()

        if include_nav:
            st.markdown("<hr style='margin:8px 0;border-color:rgba(124,124,235,0.15);' />", unsafe_allow_html=True)
            current_page = st.session_state.get("page", "dashboard")
            for label, target in menu:
                active = current_page == target
                if st.button(label, key=f"side_{target}", use_container_width=True,
                             type="primary" if active else "secondary"):
                    st.session_state.page = target
                    st.rerun()

            st.markdown("<hr style='margin:10px 0;border-color:rgba(124,124,235,0.15);' />", unsafe_allow_html=True)
            if st.button(t("nav_logout"), key="side_logout", use_container_width=True, type="secondary"):
                auth.logout_user()


def render_app_navigation():
    """Render app navigation menu inside sidebar."""
    menu = [
        (t("nav_dashboard"), "dashboard"),
        (t("nav_checkin"), "checkin"),
        (t("nav_chat"), "chat"),
        (t("nav_journal"), "journal"),
        (t("nav_wellness_tips"), "wellness_tips"),
        (t("nav_insights"), "insights"),
        (t("nav_resources"), "resources"),
        (t("nav_professional_support"), "professional_support"),
    ]
    current_page = st.session_state.get("page", "dashboard")
    with st.sidebar.expander("📌 App Navigation", expanded=False):
        for label, target in menu:
            active = current_page == target
            if st.button(label, key=f"side_nav_{target}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.page = target
                st.rerun()

        st.markdown("<hr style='margin:8px 0;border-color:rgba(124,124,235,0.15);' />", unsafe_allow_html=True)
        if st.button(t("nav_logout"), key="side_nav_logout", use_container_width=True, type="secondary"):
            auth.logout_user()
