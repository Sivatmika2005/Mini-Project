"""Landing page (marketing homepage)."""
import base64
import os
import streamlit as st
from components.navbar import render_navbar

ROBOT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "robot", "robot.svg")


def _load_robot_svg():
    with open(ROBOT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def render():
    render_navbar(logged_in=bool(st.session_state.get("user")))

    robot_svg = _load_robot_svg()
    b64 = base64.b64encode(robot_svg.encode("utf-8")).decode("utf-8")
    robot_img = (
        f"<img src='data:image/svg+xml;base64,{b64}' alt='AI wellness robot mascot' "
        "style='width:100%;max-width:380px;display:block;margin:0 auto;' />"
    )

    hero_col1, hero_col2 = st.columns([1.15, 0.85], gap="medium", vertical_alignment="center")
    with hero_col1:
        st.markdown(
            """
            <div class='hero-tagline'>AI-Powered Mental Wellness</div>
            <h1 style='color:#000000 !important;'>Your Mental<br/>Wellness Companion</h1>
            <p class='subtitle' style='color:#000000 !important;'>Track your emotions, understand your mood, and improve your
            mental well-being with AI-powered insights and support.</p>
            """,
            unsafe_allow_html=True,
        )
        action_col1, action_col2 = st.columns([1, 1], gap="small", vertical_alignment="center")
        with action_col1:
            if st.button("Start Your Journey", key="hero_checkin", use_container_width=True):
                st.session_state.page = "login" if not st.session_state.get("user") else "checkin"
                st.rerun()
        with action_col2:
            if st.button("Explore Features", key="hero_learn", type="secondary", use_container_width=True):
                st.session_state.page = "resources"
                st.rerun()
        st.markdown(
            "<div class='aw-badge'>🔒 100% Private &amp; Secure • HIPAA-Compliant</div>",
            unsafe_allow_html=True,
        )
    with hero_col2:
        st.markdown(f"<div style='text-align:center;display:flex;align-items:center;justify-content:center;min-height:100%;'>{robot_img}</div>", unsafe_allow_html=True)

    # Stats/Trust Section
    stats_col1, stats_col2, stats_col3 = st.columns(3, gap="medium", vertical_alignment="center")
    with stats_col1:
        st.markdown("<div class='aw-stat-item'><div class='aw-stat-number'>24/7</div><div class='aw-stat-label'>AI Support</div></div>", unsafe_allow_html=True)
    with stats_col2:
        st.markdown("<div class='aw-stat-item'><div class='aw-stat-number'>100%</div><div class='aw-stat-label'>Private</div></div>", unsafe_allow_html=True)
    with stats_col3:
        st.markdown("<div class='aw-stat-item'><div class='aw-stat-number'>Free</div><div class='aw-stat-label'>To Use</div></div>", unsafe_allow_html=True)


    st.markdown(
        "<div class='aw-section-title' style='text-align:center;'>Comprehensive Features</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='aw-muted' style='text-align:center;margin-top:-6px;margin-bottom:24px;'>"
        "Everything you need to check in with yourself, every day.</p>",
        unsafe_allow_html=True,
    )

    features = [
        ("💬", "AI Chat Support", "Talk it through with an empathetic AI companion, anytime you need support."),
        ("📈", "Mood Tracking", "Log your mood, stress, and energy to spot patterns over time."),
        ("📔", "Personal Journal", "Write freely and revisit your reflections whenever you like."),
        ("🌱", "Wellness Tips", "Breathing, grounding, and mindfulness exercises on demand."),
        ("🔎", "Progress Insights", "See non-diagnostic trends that help you understand yourself."),
    ]
    cols = st.columns(5, gap="small")
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(
                f"""
                <div class="aw-feature-card">
                    <div class="aw-feature-icon">{icon}</div>
                    <div style="font-weight:700;margin-bottom:4px;font-size:0.95rem;">{title}</div>
                    <div class="aw-muted" style="font-size:0.82rem;line-height:1.45;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # How it works section
    st.markdown("<div class='aw-section-title' style='text-align:center;margin-top:40px;'>How It Works</div>", unsafe_allow_html=True)
    st.markdown("<p class='aw-muted' style='text-align:center;margin-top:-6px;margin-bottom:24px;'>Get started in three simple steps</p>", unsafe_allow_html=True)
    
    steps_col1, steps_col2, steps_col3 = st.columns(3, gap="medium")
    with steps_col1:
        st.markdown("<div class='aw-step-card'><div class='aw-step-number'>1</div><div class='aw-step-title'>Create Account</div><div class='aw-step-desc'>Sign up in seconds with just your email and password</div></div>", unsafe_allow_html=True)
    with steps_col2:
        st.markdown("<div class='aw-step-card'><div class='aw-step-number'>2</div><div class='aw-step-title'>Daily Check-In</div><div class='aw-step-desc'>Log your mood, stress levels, and thoughts each day</div></div>", unsafe_allow_html=True)
    with steps_col3:
        st.markdown("<div class='aw-step-card'><div class='aw-step-number'>3</div><div class='aw-step-title'>Track Progress</div><div class='aw-step-desc'>View insights and patterns to understand yourself better</div></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="aw-card" style="text-align:center;margin-top:32px;padding:20px;">
            <div style="font-size:0.85rem;" class="aw-muted">
            <strong>Important:</strong> AI Wellness is a supportive tool, not a medical service. It does not diagnose
            conditions or replace licensed therapists or doctors. If you're in crisis, please
            see the Resources page for professional help.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
