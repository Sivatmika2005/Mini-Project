"""Resources page: mental health articles, emergency helplines, guided tools, and FAQs."""
import streamlit as st
from components.navbar import render_navbar
from components.sidebar import render_sidebar

HELPLINES = [
    ("🚨 Emergency Services (US)", "Call 911 for immediate danger or medical emergencies.", "Call 911"),
    ("📞 988 Suicide & Crisis Lifeline (US & Canada)", "Call or Text 988 (Available 24/7, Free & Confidential).", "Call/Text 988"),
    ("💬 Crisis Text Line", "Text HOME to 741741 to connect with a crisis counselor 24/7.", "Text 741741"),
    ("🇮🇳 Vandrevala Foundation (India)", "24/7 Mental Health Helpline: +91 9999 666 555.", "Call +91 9999666555"),
    ("🇮🇳 NIMHANS Toll-Free (India)", "Toll-free 24/7 helpline: 080-46110007.", "Call 080-46110007"),
    ("🇬🇧 NHS Mental Health (UK)", "Call 111 for urgent mental health support.", "Call 111"),
    ("🌐 International Helplines", "Find support in your country at https://findahelpline.com/", "findahelpline.com")
]


def render():
    if st.session_state.get("user"):
        render_sidebar()
        back_target = "dashboard"
        back_label = "Back to Dashboard"
    else:
        render_navbar(logged_in=False)
        back_target = "landing"
        back_label = "Back to Home"

    top_col1, top_col2 = st.columns([3, 1], vertical_alignment="center")
    with top_col1:
        st.markdown("<h2 style='margin-bottom:0;'>Wellness Resources &amp; Support Hub ☎️</h2>", unsafe_allow_html=True)
    with top_col2:
        if st.button(f"← {back_label}", key="resources_back", use_container_width=True, type="secondary"):
            st.session_state.page = back_target
            st.rerun()

    # Red Urgent Disclaimer
    st.markdown(
        """
        <div class="aw-card" style="border-left:5px solid #ff6b8b;background:#fff5f6;margin-bottom:20px;">
        <b style="color:#d63031;font-size:1.05rem;">⚠️ Immediate Crisis Notice:</b><br/>
        AI Wellness Companion is an automated self-help tool, <b>not clinical healthcare or medical treatment</b>.
        If you or someone you know is in immediate danger or experiencing thoughts of self-harm, please contact 24/7 emergency services or a crisis helpline immediately.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Search Bar
    query = st.text_input("🔎 Search Resources", placeholder="Search by topic: anxiety, helplines, sleep, depression...", key="res_search")

    tabs = st.tabs(["🚨 24/7 Crisis Helplines", "📚 Articles & Guides", "🧘 Mindfulness & Breathing", "❓ Frequently Asked Questions"])

    with tabs[0]:
        st.markdown("### Emergency 24/7 Helplines")
        for title, desc, action in HELPLINES:
            if not query or query.lower() in title.lower() or query.lower() in desc.lower():
                st.markdown(
                    f"""
                    <div class='aw-card' style='margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;'>
                        <div>
                            <div style='font-weight:700;font-size:1.05rem;color:#1a1a2e;'>{title}</div>
                            <div class='aw-muted' style='font-size:0.9rem;margin-top:4px;'>{desc}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tabs[1]:
        st.markdown("### Mental Health Articles & Psychoeducation")
        articles = [
            ("Understanding Stress vs Anxiety", "Anxiety is a sustained emotional response to perceived threats, while stress is usually triggered by immediate external pressure. Learning to distinguish them helps tailor self-care."),
            ("Navigating Burnout Recovery", "Burnout develops gradually through chronic overwork. Recovery requires clear boundaries, adequate physical sleep, digital detoxification, and reconnecting with hobbies."),
            ("Cognitive Reframing Techniques", "Identify automatic negative thoughts (ANTs). Ask yourself: Is this thought based on factual evidence or emotion? What is a more balanced perspective?"),
            ("Sleep Hygiene & Circadian Rhythms", "Consistent sleep schedules anchor your body clock. Keep your room dark, avoid screens 45 minutes before sleep, and view morning sunlight within 30 minutes of waking.")
        ]
        for a_title, a_body in articles:
            if not query or query.lower() in a_title.lower() or query.lower() in a_body.lower():
                with st.expander(f"📖 {a_title}"):
                    st.write(a_body)

    with tabs[2]:
        st.markdown("### Guided Relaxation & Mindfulness Tools")
        st.markdown(
            """
            <div class='aw-card'>
                <h4>4-7-8 Parasympathetic Breathing Exercise</h4>
                <p class='aw-muted'>1. Exhale completely through your mouth.<br/>
                2. Inhale quietly through your nose for <b>4 seconds</b>.<br/>
                3. Hold your breath for <b>7 seconds</b>.<br/>
                4. Exhale audibly through your mouth for <b>8 seconds</b>.<br/>
                Repeat for 4 complete cycles.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tabs[3]:
        st.markdown("### Frequently Asked Questions")
        faqs = [
            ("Is my check-in and chat data private?", "Yes. All check-ins and journal entries are stored locally on your device in your SQLite database session. We do not sell or transmit your personal reflections."),
            ("Can the AI replace a professional therapist?", "No. The AI Wellness Companion provides automated emotional reflection and coping strategies. It is not licensed to provide medical diagnosis, therapy, or prescriptions."),
            ("How does the emotion detection work?", "The app uses an internal Machine Learning Emotion Classifier that analyzes text sentiment across core emotional dimensions (Happy, Calm, Neutral, Sad, Anxious, Angry, Stressed).")
        ]
        for q_title, q_ans in faqs:
            with st.expander(f"❓ {q_title}"):
                st.write(q_ans)

