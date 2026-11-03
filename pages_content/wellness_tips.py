"""Wellness tips page: breathing, meditation, grounding, sleep, stress, affirmations and dynamic recommendations."""
import streamlit as st
from components.sidebar import render_sidebar
from utils import db, auth

AFFIRMATIONS = [
    "I am allowed to take up space and rest.",
    "I am doing the best I can with what I have today.",
    "My feelings are valid, and they will pass.",
    "I choose to be kind to myself.",
    "Progress is still progress, no matter how small.",
]


def render():
    render_sidebar()
    user = st.session_state.user

    top_col1, top_col2 = st.columns([3, 1], vertical_alignment="center")
    with top_col1:
        st.markdown("<h2 style='margin-bottom:0;'>Wellness Tips 🌱</h2>", unsafe_allow_html=True)
    with top_col2:
        if st.button("← Dashboard", key="wellness_tips_back", use_container_width=True, type="secondary"):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("<p class='aw-muted'>General wellness practices and personalized reflections — not a substitute for clinical care.</p>", unsafe_allow_html=True)

    # 1. Dynamic Recommendation Banner based on User Data
    latest_checkin = db.get_latest_checkin(user["id"])
    if latest_checkin:
        mood = latest_checkin.get("mood", "Calm")
        stress = latest_checkin.get("stress_level", 5)
        energy = latest_checkin.get("energy_level", 5)
        sleep = latest_checkin.get("sleep_quality", "Fair")

        st.markdown(
            f"""
            <div class='aw-card' style='background:linear-gradient(135deg, rgba(236,235,255,0.7), rgba(233,249,240,0.8));border:1.5px solid rgba(124,124,235,0.25);margin-bottom:20px;'>
                <div style='font-weight:700;font-size:1.05rem;color:#7c7ceb;margin-bottom:4px;'>🤖 Dynamic Recommendation for You Today</div>
                <div style='font-size:0.92rem;color:#1a1a2e;line-height:1.5;'>
                    Based on your latest check-in (<b>{mood}</b>, Stress: <b>{stress}/10</b>, Energy: <b>{energy}/10</b>, Sleep: <b>{sleep}</b>):
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if stress >= 7:
            st.info("⚡ **Stress Priority**: Your stress level is elevated. We strongly recommend trying the **Box Breathing (4-4-4-4)** or **5-4-3-2-1 Grounding** tab right now.")
        elif energy <= 4:
            st.info("🔋 **Energy Priority**: You reported low energy. Try the **3-Minute Meditation** or check out the **Sleep** hygiene guide below.")
        else:
            st.success("✨ **Balance Priority**: You are in a balanced mood state! Read through the **Positive Affirmations** to strengthen your mindset.")
    else:
        st.info("💡 **Tip**: Log a **Daily Check-In** to unlock customized daily recommendations tailored specifically to your stress and energy levels!")

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    tabs = st.tabs(["🫁 Breathing", "🧘 Meditation", "🖐️ Grounding", "🌙 Sleep", "⚡ Stress Management", "✨ Affirmations"])

    with tabs[0]:
        st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
        st.markdown("#### Box Breathing Technique (4-4-4-4)")
        st.write(
            "1. Breathe in slowly through your nose for **4 seconds**.\n"
            "2. Hold your breath gently for **4 seconds**.\n"
            "3. Breathe out slowly through your mouth for **4 seconds**.\n"
            "4. Hold for **4 seconds** before breathing in again.\n\n"
            "Repeat for 4-6 cycles. This activates the vagus nerve and lowers heart rate."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[1]:
        st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
        st.markdown("#### 3-Minute Reset Meditation")
        st.write(
            "Find a comfortable posture and unclamp your jaw.\n\n"
            "- **Minute 1**: Simply observe your natural breath without attempting to change it.\n"
            "- **Minute 2**: Scan your body from forehead to toes, releasing shoulder tension.\n"
            "- **Minute 3**: Silently repeat a grounding phrase: *'I am present, safe, and capable.'*\n\n"
            "Gently open your eyes when ready."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[2]:
        st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
        st.markdown("#### 5-4-3-2-1 Sensory Grounding")
        st.write(
            "Acknowledge surroundings to pull focus away from anxious thoughts:\n"
            "- **5** objects you can see around you\n"
            "- **4** textures or objects you can touch\n"
            "- **3** distinct sounds you can hear\n"
            "- **2** scents you can smell\n"
            "- **1** taste or positive thought\n"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[3]:
        st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
        st.markdown("#### Sleep Hygiene Essentials")
        st.write(
            "- Maintain consistent sleep/wake times daily.\n"
            "- Stop screen exposure 45 minutes before sleep.\n"
            "- Keep bedroom ambient temperature cool and dark.\n"
            "- Avoid caffeine after 2:00 PM.\n"
            "- If awake past 20 minutes, move to another room and read until sleepy."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[4]:
        st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
        st.markdown("#### Practical Stress Reduction")
        st.write(
            "- Break complex goals into bite-sized 15-minute micro-tasks.\n"
            "- Schedule mandatory 5-minute walking breaks during work.\n"
            "- Share feelings with a friend, journal, or the AI Wellness Chat.\n"
            "- Limit continuous news/social media scrolling.\n"
            "- Prioritize basic physical needs: hydration, nourishment, rest."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[5]:
        st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
        st.markdown("#### Positive Affirmations")
        for a in AFFIRMATIONS:
            st.markdown(f"<p class='aw-quote'>“{a}”</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

