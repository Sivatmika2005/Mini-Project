"""Journal page: write, view, search, and analyze entries."""
import streamlit as st
from components.sidebar import render_sidebar
from utils import db, llm
from utils.emotion_classifier import predict_emotion

CATEGORIES = ["General Reflection", "Gratitude", "Stress Release", "Daily Check-In", "Personal Growth"]
MOOD_OPTIONS = ["😊 Happy", "😌 Calm", "😐 Neutral", "😔 Sad", "😰 Anxious", "😡 Angry", "😫 Stressed"]


def render():
    render_sidebar()
    user = st.session_state.user

    top_col1, top_col2 = st.columns([3, 1], vertical_alignment="center")
    with top_col1:
        st.markdown("<h2 style='margin-bottom:0;'>Personal Journal 📔</h2>", unsafe_allow_html=True)
    with top_col2:
        if st.button("← Dashboard", key="journal_back", use_container_width=True, type="secondary"):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("<p class='aw-muted'>A private space to express your thoughts, process feelings, and log daily reflections.</p>", unsafe_allow_html=True)

    # 1. New Entry Form
    st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
    st.markdown("<div class='aw-section-title'>Write New Reflection</div>", unsafe_allow_html=True)
    
    with st.form("journal_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Title (optional)", placeholder="e.g. Evening Reflections")
        with c2:
            category = st.selectbox("Category", options=CATEGORIES)
            
        mood_tag = st.select_slider("Mood Tag", options=MOOD_OPTIONS, value="😌 Calm")
        content = st.text_area("What's on your mind today?", height=140, placeholder="Write freely without judgment...")
        
        submitted = st.form_submit_button("Save Reflection Entry →", type="primary", use_container_width=True)
        if submitted:
            if not content.strip():
                st.error("Please write something before saving your entry.")
            else:
                db.add_journal_entry(
                    user_id=user["id"],
                    title=title.strip() or f"{category} Entry",
                    content=content.strip(),
                    mood=mood_tag,
                    category=category
                )
                st.success("Reflection entry saved successfully! 🌿")
                st.rerun()
                
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
    entries = db.get_journal_entries(user["id"])

    st.markdown("### Your Journal History")

    # Search & Filter controls
    s_col1, s_col2 = st.columns([2.5, 1.5])
    with s_col1:
        search_query = st.text_input("🔎 Search entries", placeholder="Filter by title or keyword...", label_visibility="collapsed")
    with s_col2:
        selected_cat = st.selectbox("Filter Category", options=["All Categories"] + CATEGORIES, label_visibility="collapsed")

    # Filter logic
    filtered_entries = entries
    if search_query.strip():
        q = search_query.strip().lower()
        filtered_entries = [e for e in filtered_entries if q in e["title"].lower() or q in e["content"].lower()]
    if selected_cat != "All Categories":
        filtered_entries = [e for e in filtered_entries if e.get("category") == selected_cat]

    # AI Summary Banner
    if entries and len(entries) >= 2:
        with st.expander("✨ Generate AI Journal Summary"):
            if st.button("Analyze & Summarize Recent Journals", key="ai_sum_journal"):
                recent_text = "\n".join([f"- {e['title']}: {e['content'][:120]}" for e in entries[:5]])
                with st.spinner("Analyzing emotional patterns..."):
                    summary = llm.get_chat_response(
                        user_message=f"Summarize these journal entries and provide 2 gentle insights:\n{recent_text}",
                        history=[]
                    )
                st.info(f"**AI Summary Insights**:\n\n{summary}")

    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

    if not filtered_entries:
        st.markdown("<p class='aw-muted' style='padding:12px;'>No matching journal entries found.</p>", unsafe_allow_html=True)

    for entry in filtered_entries:
        date_str = entry["created_at"][:16].replace("T", " ")
        mood_str = entry.get("mood", "")
        cat_str = entry.get("category", "General")
        
        # Sentiment prediction
        emo = predict_emotion(entry["content"])

        header_label = f"📔 {entry['title']}  ·  {date_str}  ·  [{cat_str}] {mood_str}"
        with st.expander(header_label):
            st.markdown(f"<div style='font-size:0.98rem;line-height:1.65;color:#1a1a2e;'>{entry['content']}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:10px 0;border-color:rgba(124,124,235,0.12);' />", unsafe_allow_html=True)
            st.markdown(
                f"<div style='font-size:0.8rem;color:#5c5b78;'>"
                f"✨ Sentiment Analysis: <b>{emo['emotion'].capitalize()}</b> ({emo['confidence']:.0%} confidence)</div>",
                unsafe_allow_html=True,
            )
            
            if st.button("Delete Entry", key=f"del_j_{entry['id']}", type="secondary"):
                db.delete_journal_entry(entry["id"], user["id"])
                st.success("Entry deleted.")
                st.rerun()

