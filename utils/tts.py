"""Text-to-Speech (TTS) Voice Synthesis Utility for AI Wellness Companion.

Supports both gTTS (Google Text-to-Speech) audio generation and clean speech text extraction.
"""
import base64
import io
import re

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
    except Exception:
        return ""
