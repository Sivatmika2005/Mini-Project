"""Authenticated user dashboard with full multi-language translation support."""
import random
import datetime
import json
import pandas as pd
import streamlit as st
from components.sidebar import render_sidebar
from utils import db, auth, llm
from utils.translations import t

try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

MOOD_EMOJI = {
    "Happy": "😊", "Calm": "😌", "Neutral": "😐", "Sad": "😔",
    "Anxious": "😰", "Angry": "😡", "Stressed": "😫",
}


def _calculate_streak(checkins):
    if not checkins:
        return 0
    dates = sorted(list(set(c["created_at"][:10] for c in checkins)), reverse=True)
    today_str = datetime.date.today().isoformat()
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    if dates[0] != today_str and dates[0] != yesterday_str:
        return 0

    streak = 0
    curr = datetime.date.today() if dates[0] == today_str else datetime.date.today() - datetime.timedelta(days=1)

    date_set = set(dates)
    while curr.isoformat() in date_set:
        streak += 1
        curr -= datetime.timedelta(days=1)
    return streak


def render():
    render_sidebar()
    user = st.session_state.user
    greeting = auth.get_user_greeting(user.get("username", ""))

    st.markdown(f"<h2>{greeting}</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='aw-quote'>{t('dash_quote')}</p>",
        unsafe_allow_html=True,
    )

    latest = db.get_latest_checkin(user["id"])
    checkins = db.get_checkins(user["id"])
    journals = db.get_journal_entries(user["id"])
    streak_count = _calculate_streak(checkins)

    # Calculate Wellness Score
    wellness_score = 70
    if checkins:
        latest_stress = latest["stress_level"] if latest else 5
        latest_energy = latest["energy_level"] if latest else 5
        wellness_score = min(100, max(20, round(100 - (latest_stress * 6) + (latest_energy * 4))))

    # KPI Summary Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        mood = latest["mood"] if latest else "—"
        st.markdown(
            f"<div class='aw-card' style='text-align:center;padding:16px;'>"
            f"<div class='aw-muted' style='font-size:0.82rem;'>{t('dash_todays_mood')}</div>"
            f"<div style='font-size:1.5rem;font-weight:800;margin-top:4px;'>{MOOD_EMOJI.get(mood,'')} {mood}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='aw-card' style='text-align:center;padding:16px;'>"
            f"<div class='aw-muted' style='font-size:0.82rem;'>{t('dash_wellness_score')}</div>"
            f"<div style='font-size:1.5rem;font-weight:800;color:var(--accent, #7c7ceb);margin-top:4px;'>🌿 {wellness_score}/100</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c3:
        stress = latest["stress_level"] if latest else "—"
        st.markdown(
            f"<div class='aw-card' style='text-align:center;padding:16px;'>"
            f"<div class='aw-muted' style='font-size:0.82rem;'>{t('dash_stress_level')}</div>"
            f"<div style='font-size:1.5rem;font-weight:800;margin-top:4px;'>⚡ {stress}/10</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"<div class='aw-card' style='text-align:center;padding:16px;'>"
            f"<div class='aw-muted' style='font-size:0.82rem;'>{t('dash_checkin_streak')}</div>"
            f"<div style='font-size:1.5rem;font-weight:800;color:#ff6b8b;margin-top:4px;'>🔥 {streak_count}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f"<div class='aw-card' style='text-align:center;padding:16px;'>"
            f"<div class='aw-muted' style='font-size:0.82rem;'>{t('dash_journal_entries')}</div>"
            f"<div style='font-size:1.5rem;font-weight:800;margin-top:4px;'>📔 {len(journals)}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # Voice & Text AI Wellness Companion Backend Logic
    # ----------------------------------------------------
    voice_input = st.query_params.get("voice_input")
    typed_input = st.session_state.get("robo_typed_input")
    user_prompt = None

    if voice_input:
        user_prompt = voice_input.strip()
        try:
            del st.query_params["voice_input"]
        except Exception:
            pass
    elif typed_input:
        user_prompt = typed_input.strip()
        st.session_state.robo_typed_input = None

    just_processed_prompt = False

    if user_prompt:
        lower_prompt = user_prompt.lower().strip()
        nav_target = None
        if any(k in lower_prompt for k in ["check in", "checkin", "daily check", "mood check"]):
            nav_target = "checkin"
        elif any(k in lower_prompt for k in ["chat", "ai chat", "talk to ai"]) and any(k in lower_prompt for k in ["go", "open", "take", "switch", "show"]):
            nav_target = "chat"
        elif any(k in lower_prompt for k in ["journal", "diary", "reflection"]) and any(k in lower_prompt for k in ["go", "open", "take", "switch", "show"]):
            nav_target = "journal"
        elif any(k in lower_prompt for k in ["wellness tips", "tips", "breathing", "exercise", "grounding"]) and any(k in lower_prompt for k in ["go", "open", "take", "switch", "show"]):
            nav_target = "wellness_tips"
        elif any(k in lower_prompt for k in ["insight", "analytics", "trend", "stat"]) and any(k in lower_prompt for k in ["go", "open", "take", "switch", "show"]):
            nav_target = "insights"
        elif any(k in lower_prompt for k in ["resource", "helpline", "crisis"]) and not any(k in lower_prompt for k in ["doctor", "psychiatrist"]) and any(k in lower_prompt for k in ["go", "open", "take", "switch", "show"]):
            nav_target = "resources"
        elif any(k in lower_prompt for k in ["psychiatrist", "doctor", "professional support", "therapist"]) and any(k in lower_prompt for k in ["go", "open", "take", "switch", "show", "find", "see"]):
            nav_target = "professional_support"
        elif any(k in lower_prompt for k in ["profile", "setting", "preference", "account"]) and any(k in lower_prompt for k in ["go", "open", "take", "switch", "show"]):
            nav_target = "profile"
        elif any(k in lower_prompt for k in ["dashboard", "home"]) and any(k in lower_prompt for k in ["go", "open", "take", "switch", "show"]):
            nav_target = "dashboard"

        if nav_target:
            st.session_state.page = nav_target
            st.rerun()

        # 1. Get or create active conversation
        conversations = db.get_conversations(user["id"])
        if conversations:
            active_conv_id = conversations[0]["id"]
        else:
            active_conv_id = db.create_conversation(user["id"], title="Voice Reflection")

        # 2. Get history and mood context
        history = db.get_conversation_messages(active_conv_id, user["id"])
        history_formatted = [{"role": m["role"], "content": m["content"]} for m in history]

        latest_checkin = db.get_latest_checkin(user["id"])
        stress_lvl = latest_checkin["stress_level"] if latest_checkin else None
        mood_context = f"Most recent mood: {latest_checkin['mood']}, stress {latest_checkin['stress_level']}/10" if latest_checkin else ""

        journal_entries = db.get_journal_entries(user["id"])
        journal_sum = journal_entries[0].get("title") or journal_entries[0].get("content", "")[:60] if journal_entries else ""

        # 3. Call LLM chat response engine
        ai_reply = llm.get_chat_response(
            user_message=user_prompt,
            history=history_formatted,
            mood_context=mood_context,
            stress_level=stress_lvl,
            journal_summary=journal_sum,
        )

        # 4. Save user & assistant messages to database
        db.add_conversation_message(active_conv_id, user["id"], "user", user_prompt)
        db.add_conversation_message(active_conv_id, user["id"], "assistant", ai_reply)

        # 5. Store session state for UI display & SpeechSynthesis
        st.session_state.voice_user_text = user_prompt
        st.session_state.voice_ai_text = ai_reply
        st.session_state.voice_should_speak = True
        just_processed_prompt = True

    # Companion Speech Bubble Content
    if "voice_ai_text" not in st.session_state or not st.session_state.voice_ai_text:
        conversations = db.get_conversations(user["id"])
        if conversations:
            active_conv_id = conversations[0]["id"]
            history = db.get_conversation_messages(active_conv_id, user["id"])
            if history:
                assistant_msgs = [m for m in history if m.get("role") == "assistant"]
                user_msgs = [m for m in history if m.get("role") == "user"]
                if assistant_msgs:
                    st.session_state.voice_ai_text = assistant_msgs[-1]["content"]
                if user_msgs:
                    st.session_state.voice_user_text = user_msgs[-1]["content"]

    current_ai_text = st.session_state.get("voice_ai_text") or "Hello! I'm your AI Wellness Companion. How are you feeling today?"
    current_user_text = st.session_state.get("voice_user_text", "")

    should_speak = just_processed_prompt or st.session_state.get("voice_should_speak", False)
    if should_speak:
        st.session_state.voice_should_speak = False
    should_speak_js = "true" if should_speak else "false"

    from utils.tts import clean_text_for_speech
    clean_spk = clean_text_for_speech(current_ai_text)
    ai_text_to_speak_json = json.dumps(clean_spk)

    # Helper function for base64 robot image
    def _get_robot_img_b64():
        import os, base64
        img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "cute_wellness_robot.jpg")
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        return ""

    robot_b64 = _get_robot_img_b64()
    username = auth.format_user_display_name(user.get("username", ""))
    img_src = f"data:image/jpeg;base64,{robot_b64}" if robot_b64 else ""
    robot_img_html = f"<img src='{img_src}' style='width: 100%; max-width: 250px; height: auto; filter: drop-shadow(0 12px 24px rgba(124, 124, 235, 0.22)); border-radius: 20px;' alt='Cute AI Wellness Robot'/>" if img_src else "<div style='font-size:8rem;'>🤖</div>"

    user_transcript_badge = f"<div style='font-size:0.82rem; color:#6366f1; font-weight:600; margin-bottom:6px;'>You said: \"{current_user_text}\"</div>" if current_user_text else ""

    import streamlit.components.v1 as components

    # Parent-page message listener for voice input submission from iframe
    # This is kept minimal: only handles VOICE_INPUT_SUBMIT (typed fallback)
    # Speech recognition itself runs inside the iframe via injected parent script
    st.markdown("""<script>
(function() {
    if (!window._wellnessVoiceListenerReady) {
        window._wellnessVoiceListenerReady = true;
        window.addEventListener("message", function(event) {
            if (!event.data) return;
            if (event.data.type === "VOICE_INPUT_SUBMIT" && event.data.text) {
                var currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set("voice_input", event.data.text);
                window.location.href = currentUrl.href;
            }
        });
    }
})();
</script>""", unsafe_allow_html=True)

    component_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{
    box-sizing: border-box;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
body {{
    margin: 0;
    padding: 0;
    background: transparent;
}}
@keyframes robotFloat {{
    0% {{ transform: translateY(0px) rotate(0deg); }}
    50% {{ transform: translateY(-8px) rotate(1deg); }}
    100% {{ transform: translateY(0px) rotate(0deg); }}
}}
@keyframes robotListenGlow {{
    0% {{ transform: scale(1.0) translateY(-4px); filter: drop-shadow(0 0 15px rgba(124, 124, 235, 0.4)); }}
    50% {{ transform: scale(1.04) translateY(-10px); filter: drop-shadow(0 0 30px rgba(255, 107, 139, 0.8)); }}
    100% {{ transform: scale(1.0) translateY(-4px); filter: drop-shadow(0 0 15px rgba(124, 124, 235, 0.4)); }}
}}
@keyframes robotThinkTilt {{
    0% {{ transform: rotate(0deg) scale(1); filter: drop-shadow(0 0 15px rgba(99, 102, 241, 0.5)); }}
    50% {{ transform: rotate(3deg) scale(1.02); filter: drop-shadow(0 0 30px rgba(99, 102, 241, 0.8)); }}
    100% {{ transform: rotate(-3deg) scale(1); filter: drop-shadow(0 0 15px rgba(99, 102, 241, 0.5)); }}
}}
@keyframes robotSpeakBounce {{
    0% {{ transform: translateY(0px) scale(1); filter: drop-shadow(0 0 20px rgba(124, 124, 235, 0.6)); }}
    25% {{ transform: translateY(-6px) scale(1.02); filter: drop-shadow(0 0 25px rgba(152, 142, 255, 0.8)); }}
    50% {{ transform: translateY(0px) scale(1); filter: drop-shadow(0 0 20px rgba(124, 124, 235, 0.6)); }}
    75% {{ transform: translateY(-4px) scale(1.01); filter: drop-shadow(0 0 25px rgba(152, 142, 255, 0.8)); }}
    100% {{ transform: translateY(0px) scale(1); filter: drop-shadow(0 0 20px rgba(124, 124, 235, 0.6)); }}
}}
@keyframes handWave {{
    0% {{ transform: rotate(0deg); }}
    25% {{ transform: rotate(18deg); }}
    50% {{ transform: rotate(-10deg); }}
    75% {{ transform: rotate(18deg); }}
    100% {{ transform: rotate(0deg); }}
}}
@keyframes pulseWaveBar {{
    0% {{ transform: scaleY(0.4); opacity: 0.4; }}
    100% {{ transform: scaleY(1.3); opacity: 1.0; }}
}}
.robot-idle {{
    animation: robotFloat 3.5s ease-in-out infinite;
}}
.robot-greeting {{
    animation: robotFloat 2.5s ease-in-out infinite;
}}
.robot-listening {{
    animation: robotListenGlow 1.2s ease-in-out infinite !important;
}}
.robot-thinking {{
    animation: robotThinkTilt 1.5s ease-in-out infinite !important;
}}
.robot-speaking {{
    animation: robotSpeakBounce 1.0s ease-in-out infinite !important;
}}
.robot-happy {{
    animation: robotSpeakBounce 1.8s ease-in-out infinite !important;
}}
.robot-error {{
    animation: robotThinkTilt 2.0s ease-in-out infinite !important;
}}
</style>
</head>
<body>
<div style="background: linear-gradient(135deg, #f5f3ff 0%, #eef2ff 50%, #f5f3ff 100%); border-radius: 28px; border: 1px solid rgba(124, 124, 235, 0.22); padding: 32px 36px; box-shadow: 0 16px 40px rgba(124, 124, 235, 0.1); position: relative; overflow: hidden;">
<div style="position: absolute; top: 20px; left: 260px; color: rgba(124, 124, 235, 0.35); font-size: 1.2rem;">✦</div>
<div style="position: absolute; top: 50px; right: 40px; color: rgba(124, 124, 235, 0.3); font-size: 1.5rem;">✨</div>
<div style="position: absolute; bottom: 80px; left: 40px; color: rgba(124, 124, 235, 0.25); font-size: 1.1rem;">✦</div>

<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 24px;">
<div style="flex: 1 1 240px; max-width: 280px; text-align: center; margin: 0 auto;">

<div id="robot-container" class="robot-greeting" style="position: relative; display: inline-block; width: 220px; text-align: center;">
    <!-- Antenna Light -->
    <div id="robot-antenna-light" style="width: 14px; height: 14px; background: #7c7ceb; border-radius: 50%; margin: 0 auto -6px auto; box-shadow: 0 0 12px #7c7ceb; transition: all 0.3s ease;"></div>
    
    <!-- Floating Hand Wave Badge for Greeting -->
    <div id="robot-hand-wave" style="position: absolute; top: -10px; right: 10px; background: #ffffff; border-radius: 12px; padding: 4px 10px; font-size: 0.85rem; font-weight: 700; color: #6366f1; box-shadow: 0 4px 12px rgba(124,124,235,0.25); display: flex; align-items: center; gap: 4px; z-index: 10; transition: all 0.3s ease;">
        <span style="display:inline-block; animation: handWave 1.2s infinite ease-in-out;">👋</span> <span id="robot-badge-text">Hi!</span>
    </div>

    <!-- Approved Cute Pastel Robot Image with Interactive State Expression Overlay -->
    <div style="position: relative; border-radius: 24px; overflow: hidden; display: inline-block;">
        {robot_img_html}
        
        <!-- Interactive Animated Expression Badge -->
        <div id="robot-face-expression" style="position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%); background: rgba(30, 27, 75, 0.82); backdrop-filter: blur(8px); border-radius: 16px; padding: 5px 14px; color: #ffffff; font-size: 1.1rem; display: flex; align-items: center; justify-content: center; gap: 6px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.22); transition: all 0.3s ease;">
            <span id="robot-face-emoji">😊</span>
            <span id="robot-state-label" style="font-size: 0.72rem; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase; color: #a5b4fc;">WELCOME</span>
        </div>
    </div>
</div>

</div>

<div style="flex: 2 1 340px;">
<div style="background: linear-gradient(90deg, #7c7ceb, #988eff); color: #ffffff; border-radius: 20px; font-weight: 700; font-size: 0.76rem; letter-spacing: 0.9px; text-transform: uppercase; padding: 6px 16px; display: inline-flex; align-items: center; gap: 6px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(124, 124, 235, 0.3);">
<span>✦</span> AI WELLNESS COMPANION
</div>

<h2 style="font-size: 2.1rem; font-weight: 800; color: #1e1b4b; margin: 0 0 10px 0; letter-spacing: -0.5px;">
Hey {username}! 👋
</h2>

<p style="color: #475569; font-size: 1rem; line-height: 1.55; margin: 0 0 16px 0;">
I'm here to listen, support, and help you feel better. You can talk to me about anything.
</p>

{user_transcript_badge}
<div id="speech-bubble-container" style="background: #ffffff; border-radius: 20px; padding: 18px 24px; box-shadow: 0 8px 24px rgba(124, 124, 235, 0.12); border: 1.5px solid rgba(124, 124, 235, 0.2); max-width: 520px; text-align: left; transition: all 0.3s ease;">
    <div style="font-size: 0.78rem; font-weight: 700; color: #7c7ceb; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
        <span>🤖 Robot Companion Response</span>
        <span id="speech-indicator" style="color: #6366f1; font-weight: 600; font-size: 0.78rem;">🔊 Spoken Aloud</span>
    </div>
    <div id="voice-speech-bubble" style="font-size: 1.05rem; font-weight: 600; color: #1e1b4b; line-height: 1.55;">
        {current_ai_text}
    </div>
    <div style="margin-top: 14px; display: flex; gap: 10px; align-items: center;">
        <button id="btn-replay-speech" type="button" style="background: #ecebff; color: #6366f1; border: 1px solid rgba(99,102,241,0.3); border-radius: 12px; padding: 8px 16px; font-weight: 700; font-size: 0.85rem; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s ease;">
            🔊 Hear Robot Speak Again
        </button>
    </div>
</div>

</div>
</div>

<div style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(124, 124, 235, 0.2); border-radius: 22px; padding: 24px 20px 20px 20px; text-align: center; margin-top: 28px; box-shadow: 0 8px 24px rgba(124, 124, 235, 0.08); backdrop-filter: blur(10px);">
<div id="voice-status-text" style="color: #64748b; font-size: 0.9rem; font-weight: 500; margin-bottom: 16px;">
Tap the microphone and start talking...
</div>

<div style="display: flex; align-items: center; justify-content: center; gap: 18px; margin-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 4px; opacity: 0.6;">
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 12px; background: #988eff; border-radius: 4px;"></span>
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 24px; background: #7c7ceb; border-radius: 4px;"></span>
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 16px; background: #6366f1; border-radius: 4px;"></span>
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 32px; background: #7c7ceb; border-radius: 4px;"></span>
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 20px; background: #988eff; border-radius: 4px;"></span>
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 10px; background: #7c7ceb; border-radius: 4px;"></span>
</div>

<div id="voice-mic-btn" style="width: 66px; height: 66px; border-radius: 50%; background: linear-gradient(135deg, #7c7ceb 0%, #6366f1 100%); display: inline-flex; align-items: center; justify-content: center; color: #ffffff; font-size: 1.6rem; box-shadow: 0 10px 25px rgba(99, 102, 241, 0.38); border: 3px solid #ffffff; cursor: pointer; user-select: none; transition: transform 0.2s ease, background 0.3s ease;">
🎙️
</div>

<div style="display: flex; align-items: center; gap: 4px; opacity: 0.6;">
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 10px; background: #7c7ceb; border-radius: 4px;"></span>
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 20px; background: #988eff; border-radius: 4px;"></span>
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 32px; background: #7c7ceb; border-radius: 4px;"></span>
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 16px; background: #6366f1; border-radius: 4px;"></span>
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 24px; background: #7c7ceb; border-radius: 4px;"></span>
<span class="voice-wave-bar" style="display:inline-block; width: 3px; height: 12px; background: #988eff; border-radius: 4px;"></span>
</div>
</div>

<div id="voice-tap-text" style="color: #4f46e5; font-size: 0.88rem; font-weight: 700; cursor: pointer; user-select: none;">
Tap to Talk
</div>

<!-- Typed Text Reply Input Box -->
<div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 16px; max-width: 440px; margin-left: auto; margin-right: auto;">
<input id="voice-text-input" type="text" placeholder="Or type your reply here..." style="flex: 1; padding: 10px 16px; border-radius: 14px; border: 1.5px solid rgba(124, 124, 235, 0.3); font-size: 0.92rem; outline: none; background: #ffffff; color: #1e1b4b; box-shadow: inset 0 2px 4px rgba(0,0,0,0.03);" />
<button id="voice-text-send-btn" type="button" style="background: linear-gradient(135deg, #7c7ceb 0%, #6366f1 100%); color: #ffffff; border: none; border-radius: 14px; padding: 10px 18px; font-weight: 700; font-size: 0.88rem; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; box-shadow: 0 4px 12px rgba(99,102,241,0.3); transition: transform 0.2s ease;">
Send 💬
</button>
</div>
</div>

<div style="font-size: 0.82rem; color: #64748b; margin-top: 18px; text-align: center; opacity: 0.9;">
🔒 Your conversations are private and secure.
</div>
</div>

<script>
(function() {{
    const micBtn = document.getElementById("voice-mic-btn");
    const tapText = document.getElementById("voice-tap-text");
    const statusText = document.getElementById("voice-status-text");
    const speechBubble = document.getElementById("voice-speech-bubble");
    const bubbleContainer = document.getElementById("speech-bubble-container");
    const speechIndicator = document.getElementById("speech-indicator");
    const replayBtn = document.getElementById("btn-replay-speech");
    const robotContainer = document.getElementById("robot-container");

    const faceEmoji = document.getElementById("robot-face-emoji");
    const stateLabel = document.getElementById("robot-state-label");
    const antennaLight = document.getElementById("robot-antenna-light");
    const handWave = document.getElementById("robot-hand-wave");
    const badgeText = document.getElementById("robot-badge-text");

    const autoSpeakText = {ai_text_to_speak_json};
    const shouldSpeak = {should_speak_js};

    function submitVoiceInput(text) {{
        try {{
            if (!document.referrer) throw new Error("Parent URL is unavailable");
            const parentUrl = new URL(document.referrer);
            parentUrl.searchParams.set("voice_input", text);
            window.top.location.href = parentUrl.href;
            return;
        }} catch (e) {{
            // Fall back to the parent message listener when the frame URL is unavailable.
            try {{
                window.parent.postMessage({{ type: "VOICE_INPUT_SUBMIT", text: text }}, "*");
            }} catch (ignored) {{}}
        }}
    }}

    function setRobotState(state) {{
        if (!robotContainer) return;
        robotContainer.className = "";
        robotContainer.classList.add("robot-" + state);

        if (state === "listening") {{
            if (faceEmoji) faceEmoji.innerText = "👂";
            if (stateLabel) stateLabel.innerText = "LISTENING";
            if (antennaLight) {{ antennaLight.style.background = "#ff6b8b"; antennaLight.style.boxShadow = "0 0 16px #ff6b8b"; }}
            if (handWave) handWave.style.display = "none";
        }} else if (state === "thinking") {{
            if (faceEmoji) faceEmoji.innerText = "🧠";
            if (stateLabel) stateLabel.innerText = "REFLECTING";
            if (antennaLight) {{ antennaLight.style.background = "#6366f1"; antennaLight.style.boxShadow = "0 0 16px #6366f1"; }}
            if (handWave) handWave.style.display = "none";
        }} else if (state === "speaking") {{
            if (faceEmoji) faceEmoji.innerText = "🗣️";
            if (stateLabel) stateLabel.innerText = "SPEAKING";
            if (antennaLight) {{ antennaLight.style.background = "#988eff"; antennaLight.style.boxShadow = "0 0 16px #988eff"; }}
            if (handWave) handWave.style.display = "none";
        }} else if (state === "happy") {{
            if (faceEmoji) faceEmoji.innerText = "✨";
            if (stateLabel) stateLabel.innerText = "SUPPORTIVE";
            if (antennaLight) {{ antennaLight.style.background = "#7c7ceb"; antennaLight.style.boxShadow = "0 0 12px #7c7ceb"; }}
            if (handWave) {{ handWave.style.display = "flex"; if (badgeText) badgeText.innerText = "Yay!"; }}
        }} else if (state === "greeting") {{
            if (faceEmoji) faceEmoji.innerText = "👋";
            if (stateLabel) stateLabel.innerText = "WELCOME";
            if (antennaLight) {{ antennaLight.style.background = "#7c7ceb"; antennaLight.style.boxShadow = "0 0 12px #7c7ceb"; }}
            if (handWave) {{ handWave.style.display = "flex"; if (badgeText) badgeText.innerText = "Hi!"; }}
        }} else if (state === "error") {{
            if (faceEmoji) faceEmoji.innerText = "🥺";
            if (stateLabel) stateLabel.innerText = "HELP";
            if (antennaLight) {{ antennaLight.style.background = "#f43f5e"; antennaLight.style.boxShadow = "0 0 16px #f43f5e"; }}
            if (handWave) handWave.style.display = "none";
        }} else {{
            if (faceEmoji) faceEmoji.innerText = "😊";
            if (stateLabel) stateLabel.innerText = "READY";
            if (antennaLight) {{ antennaLight.style.background = "#7c7ceb"; antennaLight.style.boxShadow = "0 0 12px #7c7ceb"; }}
            if (handWave) {{ handWave.style.display = "flex"; if (badgeText) badgeText.innerText = "Hi!"; }}
        }}
    }}

    function setWaveActive(active) {{
        const waveBars = document.querySelectorAll(".voice-wave-bar");
        waveBars.forEach(bar => {{
            if (active) bar.style.animation = "pulseWaveBar 0.8s infinite alternate";
            else bar.style.animation = "none";
        }});
    }}

    function getSynth() {{
        try {{
            if (window.parent && window.parent.speechSynthesis) {{
                return window.parent.speechSynthesis;
            }}
        }} catch(e) {{}}
        return ('speechSynthesis' in window) ? window.speechSynthesis : null;
    }}

    function speakText(textToSpeak) {{
        const synth = getSynth();
        if (!synth || !textToSpeak) {{
            setRobotState("idle");
            return;
        }}

        try {{
            synth.cancel();
        }} catch(e) {{}}

        setTimeout(function() {{
            try {{
                const utter = new SpeechSynthesisUtterance(textToSpeak);
                utter.rate = 0.95;
                utter.pitch = 1.0;

                let voices = [];
                try {{ voices = synth.getVoices() || []; }} catch(e) {{}}

                for (let i = 0; i < voices.length; i++) {{
                    if (voices[i].lang && voices[i].lang.startsWith('en') && (
                        voices[i].name.includes('Natural') ||
                        voices[i].name.includes('Google') ||
                        voices[i].name.includes('Samantha') ||
                        voices[i].name.includes('Zira') ||
                        voices[i].name.includes('Jenny') ||
                        voices[i].name.includes('David')
                    )) {{
                        utter.voice = voices[i];
                        break;
                    }}
                }}

                utter.onstart = function() {{
                    if (statusText) statusText.innerText = "🔊 AI Companion is speaking...";
                    if (speechIndicator) speechIndicator.innerText = "🔊 Speaking Aloud...";
                    if (bubbleContainer) {{
                        bubbleContainer.style.borderColor = "#7c7ceb";
                        bubbleContainer.style.boxShadow = "0 0 25px rgba(124, 124, 235, 0.35)";
                    }}
                    setWaveActive(true);
                    setRobotState("speaking");
                    if (micBtn) micBtn.style.boxShadow = "0 0 25px rgba(124, 124, 235, 0.85)";
                }};

                utter.onend = function() {{
                    if (speechIndicator) speechIndicator.innerText = "✨ Speech Completed";
                    if (bubbleContainer) {{
                        bubbleContainer.style.borderColor = "rgba(124, 124, 235, 0.2)";
                        bubbleContainer.style.boxShadow = "0 8px 24px rgba(124, 124, 235, 0.12)";
                    }}
                    setWaveActive(false);
                    setRobotState("happy");
                    if (micBtn) micBtn.style.boxShadow = "0 10px 25px rgba(99, 102, 241, 0.38)";
                    if (statusText) statusText.innerText = "Tap the microphone and start talking...";
                    setTimeout(function() {{ setRobotState("idle"); }}, 3500);
                }};

                utter.onerror = function(err) {{
                    if (speechIndicator) speechIndicator.innerText = "🔊 Tap button to speak";
                    if (bubbleContainer) {{
                        bubbleContainer.style.borderColor = "rgba(124, 124, 235, 0.2)";
                    }}
                    setWaveActive(false);
                    setRobotState("idle");
                    if (micBtn) micBtn.style.boxShadow = "0 10px 25px rgba(99, 102, 241, 0.38)";
                    if (statusText) statusText.innerText = "Tap the microphone and start talking...";
                }};

                synth.speak(utter);
            }} catch(e) {{
                setRobotState("idle");
            }}
        }}, 80);
    }}

    if (replayBtn) {{
        replayBtn.onclick = function() {{
            speakText(autoSpeakText);
        }};
    }}

    if (speechBubble) {{
        speechBubble.style.cursor = "pointer";
        speechBubble.title = "Click to hear AI reply aloud";
        speechBubble.onclick = function() {{
            speakText(autoSpeakText);
        }};
    }}

    window.addEventListener("message", function(event) {{
        if (event.data && event.data.type === "VOICE_STATUS_UPDATE") {{
            const data = event.data;
            if (data.state) setRobotState(data.state);
            if (data.state === "listening") setWaveActive(true);
            else if (data.state !== "listening") setWaveActive(false);

            if (data.statusText && statusText) statusText.innerText = data.statusText;
            if (data.displayText && speechBubble) speechBubble.innerText = data.displayText;

            if (micBtn) {{
                if (data.state === "listening") {{
                    micBtn.style.transform = "scale(1.15)";
                    micBtn.style.background = "linear-gradient(135deg, #ff6b8b 0%, #7c7ceb 100%)";
                    micBtn.style.boxShadow = "0 0 25px rgba(255, 107, 139, 0.8)";
                }} else {{
                    micBtn.style.transform = "scale(1)";
                    micBtn.style.background = "linear-gradient(135deg, #7c7ceb 0%, #6366f1 100%)";
                    micBtn.style.boxShadow = "0 10px 25px rgba(99, 102, 241, 0.38)";
                }}
            }}
        }}
    }});

    let activeRecognition = null;

    // Initial load state transition: Speak if requested, else show greeting
    if (shouldSpeak && autoSpeakText) {{
        speakText(autoSpeakText);
    }} else {{
        setRobotState("greeting");
    }}

    function toggleVoiceRecognition() {{
        // Stop any TTS speaking
        const synth = getSynth();
        if (synth) {{ try {{ synth.cancel(); }} catch(e) {{}} }}

        // Immediately show activity so the user knows the click registered
        if (statusText) statusText.innerText = "Starting microphone...";
        if (micBtn) {{
            micBtn.style.transform = "scale(1.1)";
            micBtn.style.background = "linear-gradient(135deg, #ff6b8b 0%, #7c7ceb 100%)";
            micBtn.style.boxShadow = "0 0 25px rgba(255, 107, 139, 0.6)";
        }}

        // Inject a self-contained speech recognition runner into the parent document.
        // The parent page is NOT sandboxed, so SpeechRecognition + getUserMedia work there.
        var scriptCode =
            "(function() {{" +
            "  if (window._wr && window._wr.recognition) {{" +
            "    try {{ window._wr.recognition.abort(); }} catch(ignored) {{}}" +
            "    window._wr.recognition = null;" +
            "  }}" +
            "  window._wr = window._wr || {{}};" +
            "  var iframeWin = null;" +
            "  try {{" +
            "    var iframes = document.querySelectorAll('iframe');" +
            "    for (var i = 0; i < iframes.length; i++) {{" +
            "      if (iframes[i].contentWindow) {{ iframeWin = iframes[i].contentWindow; break; }}" +
            "    }}" +
            "  }} catch(e) {{}}" +
            "  function sendStatus(state, text, display) {{" +
            "    var msg = Object.assign({{}}, {{ type: 'VOICE_STATUS_UPDATE', state: state, statusText: text }});" +
            "    if (display) msg.displayText = display;" +
            "    if (iframeWin) try {{ iframeWin.postMessage(msg, '*'); }} catch(e) {{}}" +
            "  }}" +
            "  var SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;" +
            "  if (!SpeechRec) {{" +
            "    sendStatus('error', 'SpeechRecognition not supported. Use Chrome or Edge.');" +
            "    return;" +
            "  }}" +
            "  var rec = new SpeechRec();" +
            "  window._wr.recognition = rec;" +
            "  rec.continuous = false;" +
            "  rec.interimResults = true;" +
            "  rec.maxAlternatives = 1;" +
            "  var lang = navigator.language || 'en-US';" +
            "  rec.lang = lang.startsWith('en') ? lang : 'en-US';" +
            "  var submitted = false;" +
            "  rec.onstart = function() {{" +
            "    sendStatus('listening', 'Listening... Speak now.');" +
            "  }};" +
            "  rec.onaudiostart = function() {{" +
            "    sendStatus('listening', 'Microphone active - speak clearly.');" +
            "  }};" +
            "  rec.onresult = function(e) {{" +
            "    var interim = '', final_ = '';" +
            "    for (var i = e.resultIndex; i < e.results.length; i++) {{" +
            "      if (e.results[i].isFinal) final_ += e.results[i][0].transcript;" +
            "      else interim += e.results[i][0].transcript;" +
            "    }}" +
            "    var heard = (final_ || interim).trim();" +
            "    if (heard) sendStatus('listening', 'Hearing: ' + heard, heard);" +
            "    if (heard && (final_ || e.results[0].isFinal) && !submitted) {{" +
            "      submitted = true;" +
            "      window._wr.recognition = null;" +
            "      sendStatus('thinking', 'Recognized: ' + heard + '. Reflecting...', heard);" +
            "      var url = new URL(window.location.href);" +
            "      url.searchParams.set('voice_input', heard);" +
            "      window.location.href = url.href;" +
            "    }}" +
            "  }};" +
            "  rec.onerror = function(e) {{" +
            "    window._wr.recognition = null;" +
            "    var msg = 'Voice error (' + e.error + '). Tap mic to try again.';" +
            "    if (e.error === 'not-allowed' || e.error === 'permission-denied')" +
            "      msg = 'Microphone permission denied. Click the lock icon in the address bar.';" +
            "    else if (e.error === 'no-speech')" +
            "      msg = 'No speech heard. Tap the mic and speak clearly.';" +
            "    sendStatus('error', msg);" +
            "  }};" +
            "  rec.onend = function() {{" +
            "    window._wr.recognition = null;" +
            "    if (!submitted) sendStatus('idle', 'Tap the microphone and start talking...');" +
            "  }};" +
            "  try {{ rec.start(); }}" +
            "  catch(startErr) {{" +
            "    window._wr.recognition = null;" +
            "    sendStatus('error', 'Could not start: ' + (startErr.message || startErr));" +
            "  }}" +
            "}})();";

        try {{
            var parentDoc = window.parent.document;
            var old = parentDoc.getElementById("_wr_injected_script");
            if (old) old.parentNode.removeChild(old);
            var s = parentDoc.createElement("script");
            s.id = "_wr_injected_script";
            s.textContent = scriptCode;
            parentDoc.head.appendChild(s);
        }} catch(injErr) {{
            setRobotState("error");
            if (statusText) statusText.innerText = "Cannot access parent document: " + (injErr.message || injErr);
        }}
    }}

    function submitTypedReply() {{
        const input = document.getElementById("voice-text-input");
        if (!input || !input.value.trim()) return;
        const txt = input.value.trim();
        if (statusText) statusText.innerText = "🧠 AI Companion is reflecting...";
        if (speechBubble) speechBubble.innerText = "Reflecting on your words...";
        setWaveActive(false);
        setRobotState("thinking");
        input.value = "";

        submitVoiceInput(txt);
    }}

    const sendBtn = document.getElementById("voice-text-send-btn");
    const textInput = document.getElementById("voice-text-input");
    if (sendBtn) sendBtn.onclick = submitTypedReply;
    if (textInput) {{
        textInput.onkeypress = function(e) {{
            if (e.key === "Enter" || e.keyCode === 13) {{
                e.preventDefault();
                submitTypedReply();
            }}
        }};
    }}

    if (micBtn) micBtn.addEventListener("click", toggleVoiceRecognition);
    if (tapText) tapText.addEventListener("click", toggleVoiceRecognition);
}})();
</script>
</body>

</html>"""

    components.html(component_html, height=570, scrolling=False)

    robo_input = st.chat_input("💬 Type your message or reply to Robo...")
    if robo_input and robo_input.strip():
        st.session_state.robo_typed_input = robo_input.strip()
        st.rerun()

    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

    # Mini Trend & Recent Activity
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='aw-section-title'>{t('dash_recent_trend')}</div>", unsafe_allow_html=True)

        if checkins:
            df = pd.DataFrame(checkins).tail(10)
            df["created_at"] = pd.to_datetime(df["created_at"])

            if HAS_PLOTLY:
                fig = px.line(
                    df, x="created_at", y="stress_level",
                    markers=True, title=None,
                    color_discrete_sequence=["#7c7ceb"]
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=200,
                    margin=dict(l=10, r=10, t=10, b=10),
                    yaxis=dict(title="Stress Level (1-10)", range=[0, 10.5])
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.line_chart(df.set_index("created_at")["stress_level"], height=200)
        else:
            st.markdown("<p class='aw-muted' style='padding:20px 0;'>No check-in history available yet.</p>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='aw-section-title'>{t('dash_recent_history')}</div>", unsafe_allow_html=True)

        if not checkins:
            st.markdown("<p class='aw-muted' style='margin-top:8px;'>No check-ins yet.</p>", unsafe_allow_html=True)
        else:
            for entry in checkins[:4]:
                emoji = MOOD_EMOJI.get(entry["mood"], "")
                date_str = entry["created_at"][:10]
                st.markdown(
                    f"<div style='padding:8px 0;border-bottom:1px solid rgba(124,124,235,0.12);'>"
                    f"{emoji} <b>{entry['mood']}</b> · <span class='aw-muted'>Stress {entry['stress_level']}/10</span> "
                    f"<span style='float:right;' class='aw-muted'>{date_str}</span></div>",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)
