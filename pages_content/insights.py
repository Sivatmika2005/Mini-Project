"""Progress / Insights page: non-diagnostic analysis of check-in and journal history."""
import pandas as pd
import streamlit as st
from components.sidebar import render_sidebar
from utils import db, auth

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

MOOD_EMOJI = {
    "Happy": "😊", "Calm": "😌", "Neutral": "😐", "Sad": "😔",
    "Anxious": "😰", "Angry": "😡", "Stressed": "😫",
}

MOOD_SCORES = {
    "Happy": 90, "Calm": 85, "Neutral": 65, "Sad": 40,
    "Anxious": 35, "Angry": 30, "Stressed": 25
}

SLEEP_SCORES = {
    "Excellent": 100, "Good": 80, "Fair": 60, "Poor": 40, "Very Poor": 20
}


def safe_mode_str(series, default="N/A"):
    """Safely extracts mode from pandas Series without raising IndexError."""
    if series is None or series.empty or series.dropna().empty:
        return default
    m = series.mode()
    return str(m.iloc[0]) if not m.empty else default


def calculate_wellness_score(df):
    """Calculates wellness score (0-100) based on mood, stress, energy, and sleep."""
    if df.empty:
        return 70
    
    recent = df.tail(14)
    mood_vals = recent["mood"].map(lambda x: MOOD_SCORES.get(x, 60))
    stress_vals = recent["stress_level"].map(lambda s: max(0, 100 - (s * 10)))
    energy_vals = recent["energy_level"].map(lambda e: min(100, e * 10))
    sleep_vals = recent["sleep_quality"].map(lambda sl: SLEEP_SCORES.get(sl, 60))

    score = (mood_vals.mean() * 0.35) + (stress_vals.mean() * 0.30) + (energy_vals.mean() * 0.20) + (sleep_vals.mean() * 0.15)
    return round(score)


def render():
    render_sidebar()
    user = st.session_state.user

    top_col1, top_col2 = st.columns([3, 1], vertical_alignment="center")
    with top_col1:
        st.markdown("<h2 style='margin-bottom:0;'>Progress &amp; Insights 🔎</h2>", unsafe_allow_html=True)
    with top_col2:
        if st.button("← Dashboard", key="insights_back", use_container_width=True, type="secondary"):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown(
        "<p class='aw-muted'>These are general observations based on your check-ins — "
        "not a medical or diagnostic assessment.</p>",
        unsafe_allow_html=True,
    )

    checkins = db.get_checkins(user["id"])
    journals = db.get_journal_entries(user["id"])

    if not checkins:
        st.markdown(
            """
            <div class='aw-card' style='text-align:center;padding:36px;'>
                <div style='font-size:3rem;margin-bottom:12px;'>📊</div>
                <h3>No Check-Ins Recorded Yet</h3>
                <p class='aw-muted'>Complete your first daily check-in to unlock dynamic mood trends, wellness scores, and stress analytics!</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Start Your First Check-In →", key="insights_first_checkin", type="primary"):
            st.session_state.page = "checkin"
            st.rerun()
        return

    df = pd.DataFrame(checkins)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df = df.sort_values("created_at")

    avg_stress = round(df["stress_level"].mean(), 1)
    avg_energy = round(df["energy_level"].mean(), 1)
    most_common_mood = safe_mode_str(df["mood"], default="Calm")
    total_checkins = len(df)
    wellness_score = calculate_wellness_score(df)

    # 1. Summary Header KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, "Wellness Score", f"🌿 {wellness_score}/100"),
        (c2, "Avg Stress", f"⚡ {avg_stress}/10"),
        (c3, "Avg Energy", f"🔋 {avg_energy}/10"),
        (c4, "Primary Mood", f"{MOOD_EMOJI.get(most_common_mood,'')} {most_common_mood}"),
        (c5, "Total Check-ins", f"📝 {total_checkins}"),
    ]
    for col, label, val in metrics:
        with col:
            st.markdown(
                f"<div class='aw-card' style='text-align:center;padding:14px;'>"
                f"<div class='aw-muted' style='font-size:0.82rem;'>{label}</div>"
                f"<div style='font-size:1.3rem;font-weight:800;color:#1a1a2e;margin-top:4px;'>{val}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # 2. Charts Section
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("<h4 style='margin-bottom:12px;color:#1a1a2e;'>Stress &amp; Energy Trends</h4>", unsafe_allow_html=True)
        if HAS_PLOTLY:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["created_at"], y=df["stress_level"],
                mode='lines+markers', name='Stress (1-10)',
                line=dict(color='#ff6b8b', width=3),
                marker=dict(size=7)
            ))
            fig.add_trace(go.Scatter(
                x=df["created_at"], y=df["energy_level"],
                mode='lines+markers', name='Energy (1-10)',
                line=dict(color='#4ecdc4', width=3),
                marker=dict(size=7)
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=20, b=20),
                legend=dict(orientation="h", y=1.1, x=0.1),
                yaxis=dict(range=[0, 10.5]),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(df.set_index("created_at")[["stress_level", "energy_level"]])

    with col_right:
        st.markdown("<h4 style='margin-bottom:12px;color:#1a1a2e;'>Mood Distribution</h4>", unsafe_allow_html=True)
        mood_counts = df["mood"].value_counts().reset_index()
        mood_counts.columns = ["mood", "count"]
        
        if HAS_PLOTLY:
            fig_pie = px.pie(
                mood_counts, names="mood", values="count", hole=0.45,
                color_discrete_sequence=["#7c7ceb", "#b7f0d4", "#bcd9fb", "#f6c6dc", "#fbe6a5", "#4ecdc4", "#ff7675"]
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.bar_chart(mood_counts.set_index("mood"))

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # 3. Weekly Stats & AI Recommendations
    c_a, c_b = st.columns(2)

    with c_a:
        st.markdown("<h4 style='margin-bottom:8px;color:#1a1a2e;'>Weekly Trend Analysis</h4>", unsafe_allow_html=True)
        df["week"] = df["created_at"].dt.strftime("%Y-W%U")
        weekly_stress = df.groupby("week")["stress_level"].mean()
        
        if len(weekly_stress) >= 2:
            delta = weekly_stress.iloc[-1] - weekly_stress.iloc[-2]
            if delta < -0.5:
                trend_msg = "📉 **Stress Decreasing**: Your average stress dropped compared to last week — excellent progress!"
            elif delta > 0.5:
                trend_msg = "📈 **Stress Elevated**: Your average stress increased compared to last week. Try a box breathing session today."
            else:
                trend_msg = "➡️ **Stable Trend**: Your stress levels have remained steady week over week."
        else:
            trend_msg = "🌱 Continue checking in daily — multi-week trend comparison unlocks after 2 weeks of check-ins."

        st.write(trend_msg)
        
        recent = df.tail(7)
        most_recent_sleep = safe_mode_str(recent["sleep_quality"], default="Fair")
        st.markdown(f"• **Check-ins in last 7 days:** {len(recent)}")
        st.markdown(f"• **Most common sleep quality:** {most_recent_sleep}")
        st.markdown(f"• **Journal Entries Logged:** {len(journals)}")

    with c_b:
        st.markdown("<h4 style='margin-bottom:8px;color:#1a1a2e;'>Personalized Well-being Insights</h4>", unsafe_allow_html=True)
        if avg_stress >= 7:
            rec = "⚡ **High Stress Detected**: We recommend dedicating 5 minutes to the 4-7-8 Breathing Exercise under Wellness Tips."
        elif avg_energy <= 4:
            rec = "🔋 **Low Energy Pattern**: Prioritize a 15-minute afternoon walk and aim for 8 hours of restful sleep tonight."
        else:
            rec = "✨ **Balanced State**: You are maintaining a healthy emotional baseline. Keep logging your reflections!"

        st.info(rec)
        st.markdown("<div class='aw-muted' style='font-size:0.85rem;margin-top:8px;'>Reminder: Insights describe self-reported trends only and are non-diagnostic. See Resources for crisis support.</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

    # 4. Complete Check-In Data History Table (Preserved from Mood Tracker)
    st.markdown("<h4 style='margin-bottom:12px;color:#1a1a2e;'>📋 Complete Check-In History &amp; Log</h4>", unsafe_allow_html=True)
    
    display_df = df.copy()
    display_df = display_df.sort_values("created_at", ascending=False)
    display_df["Date & Time"] = display_df["created_at"].dt.strftime("%Y-%m-%d %H:%M")
    display_df["Mood"] = display_df["mood"].apply(lambda m: f"{MOOD_EMOJI.get(m, '')} {m}".strip())
    display_df["Stress Level"] = display_df["stress_level"].apply(lambda s: f"⚡ {s}/10")
    display_df["Energy Level"] = display_df["energy_level"].apply(lambda e: f"🔋 {e}/10")
    display_df["Sleep Quality"] = display_df["sleep_quality"].fillna("—")
    display_df["Journal Note"] = display_df["journal_note"].apply(lambda n: str(n).strip() if n and str(n).strip() else "—")

    cols_to_show = ["Date & Time", "Mood", "Stress Level", "Energy Level", "Sleep Quality", "Journal Note"]
    st.dataframe(display_df[cols_to_show], use_container_width=True, hide_index=True)

