"""AI wellness chatbot page with ML Emotion Intelligence & ChatGPT-style interactive 2-way dialogue."""
import datetime
import time
import streamlit as st
from components.sidebar import render_sidebar
from utils import db, llm, tts
from utils.emotion_classifier import predict_emotion


def _format_datetime(iso_str: str) -> str:
    """Format ISO timestamp into clean date-time string."""
    if not iso_str:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(iso_str)
        return dt.strftime("%b %d, %H:%M")
    except Exception:
        return iso_str[:16]


def _build_mood_context(user_id):
    latest = db.get_latest_checkin(user_id)
    if not latest:
        return ""
    return (
        f"Most recent mood: {latest['mood']}, stress {latest['stress_level']}/10, "
        f"energy {latest['energy_level']}/10, sleep quality {latest.get('sleep_quality', 'unknown')}."
    )


def _load_active_conversation(user_id):
    active_id = st.session_state.get("active_chat_id")
    if active_id is None:
        latest = db.get_latest_conversation(user_id)
        if latest:
            active_id = latest["id"]
        else:
            active_id = db.create_conversation(user_id, title="New Chat")
        st.session_state.active_chat_id = active_id

    history = db.get_conversation_messages(active_id, user_id)
    st.session_state.chat_history = [
        {"role": message["role"], "content": message["content"], "created_at": message.get("created_at", "")}
        for message in history
    ]


def _create_new_chat(user_id):
    conversation_id = db.create_conversation(user_id, title="New Chat")
    st.session_state.active_chat_id = conversation_id
    st.session_state.chat_history = []
    st.session_state.pending_delete_id = None
    st.session_state.editing_title_id = None


def _get_current_conversation_title(conversation_id, user_id):
    convs = db.get_conversations(user_id)
    for conversation in convs:
        if conversation["id"] == conversation_id:
            return conversation["title"]
    return "New Chat"


def _stream_text(text: str):
    """Generator function to simulate smooth typing streaming effect for AI response."""
    words = text.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        time.sleep(0.02)


def _group_conversations_by_date(conversations):
    """Groups user conversations into Today, Yesterday, Previous 7 Days, and Older Chats."""
    now = datetime.datetime.now()
    today_start = datetime.datetime(now.year, now.month, now.day)
    yesterday_start = today_start - datetime.timedelta(days=1)
    seven_days_ago = today_start - datetime.timedelta(days=7)

    today_chats = []
    yesterday_chats = []
    prev_7_days_chats = []
    older_chats = []

    for conv in conversations:
        dt_str = conv.get("updated_at") or conv.get("created_at")
        try:
            conv_dt = datetime.datetime.fromisoformat(dt_str)
        except Exception:
            conv_dt = now

        if conv_dt >= today_start:
            today_chats.append(conv)
        elif conv_dt >= yesterday_start:
            yesterday_chats.append(conv)
        elif conv_dt >= seven_days_ago:
            prev_7_days_chats.append(conv)
        else:
            older_chats.append(conv)

    return [
        ("Recent Chats (Today)", today_chats),
        ("Yesterday", yesterday_chats),
        ("Previous 7 Days", prev_7_days_chats),
        ("Older Chats", older_chats),
    ]


def render():
    from components.sidebar import render_app_navigation
    render_sidebar(include_nav=False)
    user = st.session_state.user

    # Header controls
    top_col1, top_col2, top_col3 = st.columns([2.5, 1.2, 1], vertical_alignment="center")
    with top_col1:
        st.markdown("<h2 style='margin-bottom:0;'>AI Wellness Chat 💬</h2>", unsafe_allow_html=True)
    with top_col2:
        auto_voice = st.toggle("🔊 Auto Voice", value=st.session_state.get("auto_read_voice", False), key="auto_read_voice_toggle")
        st.session_state.auto_read_voice = auto_voice
    with top_col3:
        if st.button("← Dashboard", key="chat_back", use_container_width=True, type="secondary"):
            st.session_state.page = "dashboard"
            st.rerun()


    if "active_chat_id" not in st.session_state or st.session_state.active_chat_id is None:
        _load_active_conversation(user["id"])

    # Dedicated ChatGPT-Style Conversation Sidebar (Renders at TOP of sidebar)
    with st.sidebar:
        st.markdown("<hr style='margin:6px 0;border-color:rgba(124,124,235,0.15);' />", unsafe_allow_html=True)
        if st.button("➕ New Chat", key="new_chat_sidebar_top", use_container_width=True, type="primary"):
            _create_new_chat(user["id"])
            st.rerun()

        conversations = db.get_conversations(user["id"])
        grouped_convs = _group_conversations_by_date(conversations)

        pending_delete = st.session_state.get("pending_delete_id")
        editing_id = st.session_state.get("editing_title_id")

        for group_title, chat_list in grouped_convs:
            if not chat_list:
                continue

            st.markdown(f"<div class='aw-section-title' style='font-size:0.85rem;margin-top:10px;margin-bottom:4px;font-weight:700;color:#7c7ceb;'>{group_title}</div>", unsafe_allow_html=True)

            for conversation in chat_list:
                c_id = conversation["id"]
                is_active = (c_id == st.session_state.get("active_chat_id"))
                date_str = _format_datetime(conversation.get("updated_at") or conversation.get("created_at"))

                # Inline Edit Mode for Rename
                if editing_id == c_id:
                    new_title = st.text_input("Rename:", value=conversation["title"], key=f"rename_input_{c_id}")
                    save_cols = st.columns(2)
                    with save_cols[0]:
                        if st.button("Save", key=f"save_title_{c_id}", use_container_width=True, type="primary"):
                            if new_title.strip():
                                db.update_conversation_title(c_id, user["id"], new_title.strip())
                            st.session_state.editing_title_id = None
                            st.rerun()
                    with save_cols[1]:
                        if st.button("Cancel", key=f"cancel_title_{c_id}", use_container_width=True):
                            st.session_state.editing_title_id = None
                            st.rerun()
                else:
                    cols = st.columns([3.2, 0.7, 0.7])
                    with cols[0]:
                        if st.button(
                            conversation["title"],
                            key=f"conv_{c_id}",
                            use_container_width=True,
                            type="primary" if is_active else "secondary",
                            help=f"Last updated: {date_str}" if date_str else None,
                        ):
                            st.session_state.active_chat_id = c_id
                            st.session_state.pending_delete_id = None
                            st.session_state.editing_title_id = None
                            _load_active_conversation(user["id"])
                            st.rerun()

                    with cols[1]:
                        if st.button("✏️", key=f"edit_{c_id}", use_container_width=True, help="Rename conversation"):
                            st.session_state.editing_title_id = c_id
                            st.rerun()

                    with cols[2]:
                        if st.button("🗑", key=f"delete_{c_id}", use_container_width=True, help="Delete conversation"):
                            st.session_state.pending_delete_id = c_id
                            st.rerun()

                # Delete Confirmation Prompt
                if pending_delete == c_id:
                    st.markdown("<div class='aw-muted' style='font-size:0.75rem;color:#e74c3c;'>Confirm Delete?</div>", unsafe_allow_html=True)
                    confirm_cols = st.columns(2)
                    with confirm_cols[0]:
                        if st.button("Delete", key=f"confirm_delete_{c_id}", use_container_width=True, type="primary"):
                            db.delete_conversation(c_id, user["id"])
                            if st.session_state.get("active_chat_id") == c_id:
                                remaining = db.get_conversations(user["id"])
                                st.session_state.active_chat_id = remaining[0]["id"] if remaining else None
                                if remaining:
                                    _load_active_conversation(user["id"])
                                else:
                                    st.session_state.chat_history = []
                            st.session_state.pending_delete_id = None
                            st.rerun()
                    with confirm_cols[1]:
                        if st.button("Cancel", key=f"cancel_delete_{c_id}", use_container_width=True):
                            st.session_state.pending_delete_id = None
                            st.rerun()

        st.markdown("<hr style='margin:14px 0;border-color:rgba(124,124,235,0.15);' />", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.75rem;text-align:center;color:#94a3b8;line-height:1.4;margin-bottom:8px;'>"
            "🔒 <b>Confidential &amp; Private</b><br>"
            "AI Companion is not a substitute for clinical care. See Resources for crisis support.</div>",
            unsafe_allow_html=True,
        )
        render_app_navigation()


    # Handle pending prompt
    prompt_to_process = None
    if st.session_state.get("pending_prompt"):
        prompt_to_process = st.session_state.pop("pending_prompt")

    user_input = st.chat_input("Type your message to AI Wellness companion...") or prompt_to_process

    # Render History
    for idx, message in enumerate(st.session_state.get("chat_history", [])):
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant", avatar="🌿"):
                st.write(message["content"])
                tts.render_tts_player(message["content"], message_key=f"msg_{idx}")

    # Process New Input with Streaming Response & Typing Status
    if user_input:
        normalized_input = user_input.strip()
        if normalized_input:
            now_str = datetime.datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append({"role": "user", "content": normalized_input, "created_at": now_str})
            db.add_conversation_message(
                st.session_state.active_chat_id,
                user["id"],
                "user",
                normalized_input,
            )

            with st.chat_message("user", avatar="👤"):
                st.write(normalized_input)

            mood_context = _build_mood_context(user["id"])
            latest_checkin = db.get_latest_checkin(user["id"])
            stress_lvl = latest_checkin["stress_level"] if latest_checkin else None

            journal_entries = db.get_journal_entries(user["id"])
            journal_sum = ""
            if journal_entries:
                first_j = journal_entries[0]
                journal_sum = first_j.get("title") or first_j.get("content", "")[:60]

            with st.chat_message("assistant", avatar="🌿"):
                with st.spinner("AI companion is reflecting..."):
                    reply = llm.get_chat_response(
                        user_message=normalized_input,
                        history=st.session_state.chat_history[:-1],
                        mood_context=mood_context,
                        stress_level=stress_lvl,
                        journal_summary=journal_sum,
                    )
                
                # Streaming typing response effect
                full_reply = st.write_stream(_stream_text(reply))

            st.session_state.chat_history.append({"role": "assistant", "content": reply, "created_at": now_str})
            db.add_conversation_message(
                st.session_state.active_chat_id,
                user["id"],
                "assistant",
                reply,
            )

            # Auto-play audio if Auto Voice is toggled ON
            if st.session_state.get("auto_read_voice"):
                st.session_state.playing_tts_key = f"msg_{len(st.session_state.chat_history)-1}"

            current_title = _get_current_conversation_title(st.session_state.active_chat_id, user["id"])
            if current_title == "New Chat":
                try:
                    title = llm.generate_chat_title(normalized_input)
                    db.update_conversation_title(st.session_state.active_chat_id, user["id"], title)
                except Exception:
                    db.update_conversation_title(st.session_state.active_chat_id, user["id"], "Daily Reflection")

            st.rerun()


