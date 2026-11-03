"""Daily mental health check-in page."""
import datetime
import time
import streamlit as st
import streamlit.components.v1 as components
from components.sidebar import render_sidebar
from utils import db, auth

MOODS = [
    ("😊", "Happy"), ("😌", "Calm"), ("😐", "Neutral"), ("😔", "Sad"),
    ("😰", "Anxious"), ("😡", "Angry"), ("😫", "Stressed"),
]


def render():
    render_sidebar()
    user = st.session_state.user

    top_col1, top_col2 = st.columns([3, 1], vertical_alignment="center")
    with top_col1:
        st.markdown("<h2 style='margin-bottom:0;'>Daily Check-In 📝</h2>", unsafe_allow_html=True)
    with top_col2:
        if st.button("← Dashboard", key="checkin_back", use_container_width=True, type="secondary"):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("<p class='aw-muted'>Take a moment for yourself. This takes about two minutes.</p>", unsafe_allow_html=True)

    # Check if user already checked in today
    today_str = datetime.date.today().isoformat()
    latest_checkin = db.get_latest_checkin(user["id"])
    has_checked_in_today = False
    if latest_checkin and latest_checkin.get("created_at", "").startswith(today_str):
        has_checked_in_today = True

    if has_checked_in_today and not st.session_state.get("checkin_saved_just_now"):
        st.info(
            f"🌱 **You've already checked in today!** Your mood was recorded as "
            f"**{latest_checkin['mood']}** (Stress: {latest_checkin['stress_level']}/10). "
            f"You can submit another check-in below to update your status."
        )

    # Progress Indicator
    selected_mood = st.session_state.get("selected_mood")
    step1_done = selected_mood is not None
    progress_val = 50 if step1_done else 15
    st.progress(progress_val, text=f"Step {'2/2: Detail Reflection' if step1_done else '1/2: Select Your Mood'}")

    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    st.markdown("### Step 1: How are you feeling today?")

    if "selected_mood" not in st.session_state:
        st.session_state.selected_mood = None

    mood_cols = st.columns(7)
    for col, (emoji, label) in zip(mood_cols, MOODS):
        with col:
            selected = st.session_state.selected_mood == label
            if st.button(
                f"{emoji}\n{label}",
                key=f"mood_{label}",
                use_container_width=True,
                type="primary" if selected else "secondary",
            ):
                st.session_state.selected_mood = label
                st.rerun()

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown("### Step 2: Reflections & Levels")

    with st.form("checkin_form", clear_on_submit=False):
        emotion_note = st.text_input("What's contributing to this feeling? (optional)", placeholder="Work, family, sleep, weather, etc.")
        
        c1, c2 = st.columns(2)
        with c1:
            stress_level = st.slider("Stress level (1 = Very Low, 10 = Severe)", 1, 10, 5)
        with c2:
            energy_level = st.slider("Energy level (1 = Exhausted, 10 = High Energy)", 1, 10, 5)
            
        sleep_quality = st.select_slider(
            "Sleep quality last night",
            options=["Very Poor", "Poor", "Fair", "Good", "Excellent"],
            value="Fair",
        )
        journal_note = st.text_area("Journal note (optional)", placeholder="Anything on your mind you'd like to reflect on...")

        submitted = st.form_submit_button("Submit Daily Check-In →", type="primary", use_container_width=True)
        if submitted:
            if not st.session_state.selected_mood:
                st.error("Please select a mood emoji above before submitting.")
            else:
                db.add_checkin(
                    user["id"],
                    st.session_state.selected_mood,
                    emotion_note,
                    stress_level,
                    energy_level,
                    sleep_quality,
                    journal_note,
                )
                
                # Also add as journal entry if journal note provided
                if journal_note and journal_note.strip():
                    db.add_journal_entry(
                        user["id"],
                        title=f"Check-In Note: {st.session_state.selected_mood}",
                        content=journal_note.strip(),
                        mood=st.session_state.selected_mood,
                        category="Check-In"
                    )

                st.session_state.checkin_saved_just_now = True
                saved_mood = st.session_state.selected_mood
                st.session_state.selected_mood = None
                st.success(f"Check-in saved! Recorded mood: **{saved_mood}**. Great job taking care of yourself today! 🌿")
                
                # SAFE AUTO-TERMINATING CELEBRATION (Max 3s, non-blocking)
                nonce = int(time.time() * 1000)
                celebration_code = f"""
                <script>
                (function() {{
                    try {{
                        const targetDoc = (window.parent && window.parent.document) ? window.parent.document : document;
                        targetDoc.querySelectorAll('.aw-celebration-root').forEach(el => el.remove());
                        
                        const overlay = targetDoc.createElement('div');
                        overlay.className = 'aw-celebration-root';
                        overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9999;overflow:hidden;';
                        
                        const canvas = targetDoc.createElement('canvas');
                        canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;';
                        overlay.appendChild(canvas);
                        targetDoc.body.appendChild(overlay);
                        
                        const ctx = canvas.getContext('2d');
                        const targetWin = (window.parent && window.parent.innerWidth) ? window.parent : window;
                        canvas.width = targetWin.innerWidth;
                        canvas.height = targetWin.innerHeight;
                        
                        const pieces = [];
                        const colors = ['#7c7ceb', '#a5a6f6', '#b7f0d4', '#bcd9fb', '#f6c6dc'];
                        for (let i = 0; i < 40; i++) {{
                            pieces.push({{
                                x: Math.random() * canvas.width,
                                y: -20,
                                size: Math.random() * 6 + 4,
                                color: colors[Math.floor(Math.random() * colors.length)],
                                speedY: Math.random() * 3 + 2,
                                speedX: (Math.random() - 0.5) * 2
                            }});
                        }}
                        
                        let start = Date.now();
                        function run() {{
                            if (Date.now() - start > 2500) {{
                                if (targetDoc.body.contains(overlay)) overlay.remove();
                                return;
                            }}
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                            pieces.forEach(p => {{
                                p.y += p.speedY;
                                p.x += p.speedX;
                                ctx.fillStyle = p.color;
                                ctx.beginPath();
                                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                                ctx.fill();
                            }});
                            requestAnimationFrame(run);
                        }}
                        requestAnimationFrame(run);
                        
                        setTimeout(() => {{
                            if (targetDoc.body.contains(overlay)) overlay.remove();
                        }}, 3000);
                    }} catch(e) {{}}
                }})();
                </script>
                """
                components.html(celebration_code, height=0)


