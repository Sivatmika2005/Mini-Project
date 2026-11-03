"""User Profile & Settings page."""
import streamlit as st
from components.sidebar import render_sidebar
from utils import db, auth
from utils.translations import t


def render():
    user = st.session_state.get("user")
    if not user:
        st.session_state.page = "login"
        st.rerun()
        return

    render_sidebar()

    if st.button(t("back_to_dashboard"), key="profile_back"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.markdown(f"<h2>{t('profile_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='aw-muted'>{t('profile_subtitle')}</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        # Profile Card
        st.markdown(
            f"""
            <div class='aw-card' style='text-align:center;padding:30px 20px;'>
                <div style='font-size:4rem;margin-bottom:12px;'>🌿</div>
                <h3 style='margin:0 0 6px 0;'>{auth.format_user_display_name(user["username"])}</h3>
                <p class='aw-muted' style='margin:0;'>✉️ {user["email"]}</p>
                <div style='margin-top:12px;display:inline-block;padding:4px 14px;background:rgba(124,124,235,0.12);border-radius:999px;font-size:0.82rem;font-weight:600;color:var(--accent, #7c7ceb);'>
                    {t('user_id_label')}: #{user["id"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

        # Edit Display Name Card
        st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='aw-section-title'>{t('edit_display_name')}</div>", unsafe_allow_html=True)

        with st.form("edit_name_form"):
            new_name = st.text_input(t("display_name_label"), value=user["username"], key="edit_username_input")
            submitted = st.form_submit_button(t("save_display_name"), type="primary", use_container_width=True)
            if submitted:
                if not new_name.strip():
                    st.error("Name cannot be empty.")
                else:
                    success, msg = db.update_user_username(user["id"], new_name)
                    if success:
                        st.session_state.user["username"] = new_name.strip()
                        st.toast("Display name updated successfully! 🌿", icon="✅")
                        st.rerun()
                    else:
                        st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Preferences Card
        st.markdown("<div class='aw-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='aw-section-title'>{t('visual_theme_settings')}</div>", unsafe_allow_html=True)
        st.markdown(f"<p class='aw-muted' style='font-size:0.88rem;'>{t('theme_subtitle')}</p>", unsafe_allow_html=True)

        settings = db.get_user_settings(user["id"])
        current_theme = st.session_state.get("theme", settings.get("theme", "Light"))
        current_lang = st.session_state.get("language", settings.get("language", "English"))

        theme_options = ["Light ☀️", "Soft Pastel 🌸", "Ocean Breeze 🌊"]
        theme_map = {
            "Light ☀️": "Light",
            "Soft Pastel 🌸": "Soft Pastel",
            "Ocean Breeze 🌊": "Ocean Breeze",
        }

        theme_index = 0
        if current_theme == "Soft Pastel":
            theme_index = 1
        elif current_theme == "Ocean Breeze":
            theme_index = 2

        selected_theme_label = st.selectbox(t("select_theme_label"), options=theme_options, index=theme_index, key="select_theme")
        selected_theme = theme_map[selected_theme_label]

        if selected_theme != current_theme:
            st.session_state.theme = selected_theme
            db.save_user_settings(user["id"], theme=selected_theme)
            st.toast(f"Theme updated to {selected_theme}! 🎨", icon="✨")
            st.rerun()

        st.markdown("<hr style='margin:24px 0;border-color:rgba(124,124,235,0.15);' />", unsafe_allow_html=True)

        # Language Card
        st.markdown(f"<div class='aw-section-title'>{t('language_preferences')}</div>", unsafe_allow_html=True)
        st.markdown(f"<p class='aw-muted' style='font-size:0.88rem;'>{t('lang_subtitle')}</p>", unsafe_allow_html=True)

        lang_options = [
            "English 🇬🇧",
            "தமிழ் 🇮🇳 (Tamil)",
        ]
        lang_map = {
            "English 🇬🇧": "English",
            "தமிழ் 🇮🇳 (Tamil)": "Tamil",
        }

        lang_index = 0
        for i, opt in enumerate(lang_options):
            if lang_map[opt] == current_lang:
                lang_index = i
                break

        selected_lang_label = st.selectbox(t("select_lang_label"), options=lang_options, index=lang_index, key="select_lang")
        selected_lang = lang_map[selected_lang_label]

        if selected_lang != current_lang:
            st.session_state.language = selected_lang
            db.save_user_settings(user["id"], language=selected_lang)
            st.toast(f"Language set to {selected_lang}! 🌐", icon="🎉")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
