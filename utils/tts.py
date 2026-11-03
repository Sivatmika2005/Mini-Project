"""Text-to-Speech (TTS) Voice Synthesis Utility for AI Wellness Companion.

Supports both gTTS (Google Text-to-Speech) audio generation and Browser Web Speech API fallback.
"""
import base64
import io
import re
import streamlit as st

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


def clean_text_for_speech(text: str) -> str:
    """Removes markdown symbols, URLs, and code blocks for smooth natural speech reading."""
    if not text:
        return ""
    
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Remove inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove Markdown headers, bold, italics, bullets
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'[*_]{1,3}([^*_]+)[*_]{1,3}', r'\1', text)
    text = re.sub(r'^\s*[-+*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_audio_base64(text: str, lang: str = "en") -> str:
    """Generates MP3 audio base64 data URI using gTTS."""
    clean = clean_text_for_speech(text)
    if not clean or not GTTS_AVAILABLE:
        return ""
    try:
        fp = io.BytesIO()
        tts = gTTS(text=clean, lang=lang, slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode("utf-8")
        return f"data:audio/mp3;base64,{b64}"
    except Exception as e:
        return ""


def speak_via_js(text: str, rate: float = 1.0):
    """Executes browser native Web Speech API (window.speechSynthesis) via HTML/JS injection."""
    clean = clean_text_for_speech(text)
    if not clean:
        return
    
    # Escape quotes and backslashes for JS string
    clean_js = clean.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
    
    js_code = f"""
    <script>
    (function() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel(); // Stop any active speech
            var utterance = new SpeechSynthesisUtterance("{clean_js}");
            utterance.rate = {rate};
            utterance.pitch = 1.0;
            
            // Try selecting a gentle female/calm voice if available
            var voices = window.speechSynthesis.getVoices();
            for (var i = 0; i < voices.length; i++) {{
                if (voices[i].lang.startsWith('en') && (voices[i].name.includes('Natural') || voices[i].name.includes('Google') || voices[i].name.includes('Samantha') || voices[i].name.includes('Zira'))) {{
                    utterance.voice = voices[i];
                    break;
                }}
            }}
            window.speechSynthesis.speak(utterance);
        }}
    }})();
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)


def stop_speech_js():
    """Stops any currently playing browser speech synthesis."""
    js_code = """
    <script>
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)


def render_tts_player(text: str, message_key: str, auto_play: bool = False):
    """Renders audio controls and handles playback for an AI chat message."""
    clean_txt = clean_text_for_speech(text)
    if not clean_txt:
        return

    # Check session state for active playback key
    is_playing = st.session_state.get("playing_tts_key") == message_key

    cols = st.columns([1, 1, 6], vertical_alignment="center")
    
    with cols[0]:
        if st.button("🔊 Listen", key=f"play_tts_{message_key}", use_container_width=True, type="secondary" if not is_playing else "primary"):
            st.session_state.playing_tts_key = message_key
            st.rerun()
            
    with cols[1]:
        if st.button("🛑 Stop", key=f"stop_tts_{message_key}", use_container_width=True):
            if st.session_state.get("playing_tts_key") == message_key:
                st.session_state.playing_tts_key = None
            stop_speech_js()
            st.rerun()

    # Trigger playback if active or auto_play
    if is_playing or auto_play:
        audio_b64 = get_audio_base64(clean_txt)
        if audio_b64:
            # HTML5 audio player with autoplay
            audio_html = f"""
            <audio autoplay controls style="width: 100%; height: 36px; margin-top: 6px; border-radius: 8px;">
                <source src="{audio_b64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        else:
            # Fallback to browser Web Speech API
            speak_via_js(clean_txt)
