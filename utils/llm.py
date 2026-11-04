"""External AI API Integration for AI Mental Wellness Companion.

Connects the AI Chat page securely to production-ready external AI APIs:
- Google Gemini API (gemini-1.5-flash / gemini-2.0-flash / gemini-1.5-pro)
- OpenAI API (gpt-4o-mini / gpt-4o)
- Groq API (llama-3.3-70b-versatile / mixtral-8x7b-32768)
- Anthropic Claude API (claude-3-5-sonnet / claude-3-haiku)

Features:
- Secure backend integration: API keys loaded exclusively from .env
- Multi-turn conversation context preservation (sliding window)
- Emotional context injection (recent mood, stress level, journal reflections)
- Immediate 24/7 crisis safety intervention protocol
- Separate dedicated responses for AI Chat vs Dashboard Robot Companion
"""
import os
import re
import json
import logging
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Mental Wellness System Prompt for External AI API
WELLNESS_SYSTEM_PROMPT = """You are a warm, empathetic, and compassionate AI Mental Wellness Companion.
Your purpose is to provide supportive, non-judgmental, active listening and evidence-informed wellness guidance for stress management, emotional balance, anxiety relief, sleep improvement, and mindful reflection.

Key Guidelines:
1. Empathy & Tone: Respond with genuine warmth, gentle validation, and conversational kindness. Speak like an understanding, compassionate guide.
2. Context Awareness: Remember previous messages in this conversation so follow-up reflections make sense naturally. Use any provided check-in or journal background to tailor your suggestions.
3. Practical Wellness: When helpful, offer evidence-based self-care techniques (e.g., 4-4-4-4 box breathing, 5-4-3-2-1 sensory grounding, cognitive reframing, gentle progressive muscle relaxation, or journaling prompts).
4. Concise & Readable: Keep answers focused, clear, and readable (3 to 6 sentences or brief bullet points). Avoid overwhelming the user with massive blocks of text.
5. Clinical Boundary: You are an AI wellness companion, NOT a medical doctor or licensed therapist. Do not diagnose mental health or psychiatric conditions or prescribe medications.
6. Safety Protocol: If the user indicates imminent self-harm, suicide, or severe crisis, express immediate calm empathy and encourage contacting trusted 24/7 crisis support lines."""

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "self harm", "self-harm", "want to die",
    "hurt myself", "end my life", "ending it all", "don't want to live",
]

CRISIS_RESPONSE = (
    "I'm really glad you reached out to me today. I can hear how much pain you're carrying right now, "
    "and please remember you do not have to navigate this alone.\n\n"
    "Because I am an AI wellness companion, I cannot provide emergency crisis care. "
    "Please connect right now with a compassionate, trained counselor who can support you 24/7:\n\n"
    "• **Tele-MANAS (Tamil Nadu & India)**: Call **14416** or **1800-891-4416** (24/7, Toll-Free, Tamil & English)\n"
    "• **Sneha Suicide Prevention (Chennai)**: Call **044-24640050** or **044-24640060** (24/7)\n"
    "• **Emergency Services (India)**: Call **112** (Police, Ambulance, Emergency)\n"
    "• **Tamil Nadu State Health Helpline**: Call **104** (24/7 Medical & Student Exam Counselling)\n"
    "• **NIMHANS Mental Health Helpline**: Call **080-46110007** (24/7 National Psychosocial Support)\n\n"
    "Please reach out to emergency services or someone you trust right now."
)


def _contains_crisis_language(text: str) -> bool:
    """Checks whether the user input contains expressions of crisis or self-harm."""
    lowered = (text or "").lower()
    return any(kw in lowered for kw in CRISIS_KEYWORDS)


def get_active_ai_provider() -> Optional[str]:
    """Identifies the configured external AI API provider based on environment variables."""
    load_dotenv(override=True)
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    elif os.getenv("OPENAI_API_KEY"):
        return "openai"
    elif os.getenv("GROQ_API_KEY"):
        return "groq"
    elif os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return None


def is_external_api_configured() -> bool:
    """Returns True if any external AI API key is configured."""
    return get_active_ai_provider() is not None


def _get_sliding_context_window(history: List[Dict], max_turns: int = 10) -> List[Dict]:
    """Retains the most recent conversation messages to maintain context within token allowances."""
    if not history:
        return []
    # Keep up to the last max_turns messages
    trimmed = []
    for msg in history[-max_turns:]:
        role = msg.get("role", "user")
        content = (msg.get("content") or "").strip()
        if content:
            trimmed.append({"role": role, "content": content})
    return trimmed


# ==============================================================================
# EXTERNAL AI API: GOOGLE GEMINI
# ==============================================================================
def _call_gemini_api(user_message: str, history: List[Dict], system_prompt: str) -> str:
    """Calls Google Gemini API with automatic model cascading to prevent 404/503 errors."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    configured_model = os.getenv("GEMINI_MODEL") or "gemini-flash-lite-latest"
    candidate_models = [
        configured_model,
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-pro-latest",
    ]
    models_to_try = []
    for m in candidate_models:
        if m and m not in models_to_try:
            models_to_try.append(m)

    headers = {"Content-Type": "application/json"}

    contents = []
    # Add historical messages in alternating user / model format
    for m in history:
        role = "user" if m.get("role") == "user" else "model"
        text = m.get("content", "").strip()
        if text:
            contents.append({"role": role, "parts": [{"text": text}]})

    # Add the current user message
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9,
            "maxOutputTokens": 800,
        },
    }

    last_error = None
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                    parts = candidates[0]["content"]["parts"]
                    text_result = "".join(p.get("text", "") for p in parts).strip()
                    if text_result:
                        return text_result
        except urllib.error.HTTPError as e:
            last_error = e
            logger.warning(f"Gemini model {model_name} returned {e.code}, attempting fallback model...")
            continue
        except Exception as e:
            last_error = e
            logger.warning(f"Gemini model {model_name} error: {e}")
            continue

    if last_error:
        raise last_error
    raise RuntimeError("No text content returned from Gemini API.")


# ==============================================================================
# EXTERNAL AI API: OPENAI & GROQ
# ==============================================================================
def _call_openai_compatible_api(user_message: str, history: List[Dict], system_prompt: str, provider: str = "openai") -> str:
    """Calls OpenAI (gpt-4o-mini) or Groq (llama-3.3-70b-versatile) completions API."""
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        url = "https://api.openai.com/v1/chat/completions"
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    else:  # groq
        api_key = os.getenv("GROQ_API_KEY")
        url = "https://api.groq.com/openai/v1/chat/completions"
        model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        raise ValueError(f"{provider.upper()}_API_KEY is not configured.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    messages = [{"role": "system", "content": system_prompt}]
    for m in history:
        role = "user" if m.get("role") == "user" else "assistant"
        content = m.get("content", "").strip()
        if content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        choices = res_data.get("choices", [])
        if choices and "message" in choices[0]:
            return choices[0]["message"].get("content", "").strip()

    raise RuntimeError(f"No response choices returned from {provider} API.")


# ==============================================================================
# EXTERNAL AI API: ANTHROPIC CLAUDE
# ==============================================================================
def _call_anthropic_api(user_message: str, history: List[Dict], system_prompt: str) -> str:
    """Calls Anthropic Messages API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not configured.")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    messages = []
    for m in history:
        role = "user" if m.get("role") == "user" else "assistant"
        content = m.get("content", "").strip()
        if content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        "max_tokens": 800,
        "system": system_prompt,
        "messages": messages,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        return "".join(b.get("text", "") for b in res_data.get("content", []) if b.get("type") == "text").strip()


# ==============================================================================
# MAIN EXTERNAL AI CHATBOT INTERFACE (EXCLUSIVELY FOR AI CHAT PAGE)
# ==============================================================================
def get_external_ai_chat_response(
    user_message: str,
    history: List[Dict] = None,
    mood_context: str = "",
    stress_level: Optional[int] = None,
    journal_summary: str = "",
) -> str:
    """Generates natural, contextual, empathetic mental wellness responses via the External AI API.

    Maintains multi-turn context across follow-up queries and safely handles crisis language.
    """
    clean_user_message = (user_message or "").strip()
    if not clean_user_message:
        return "I'm right here with you whenever you're ready to share."

    # Immediate crisis safety check
    if _contains_crisis_language(clean_user_message):
        return CRISIS_RESPONSE

    # Prepare sliding conversation history to maintain context
    trimmed_history = _get_sliding_context_window(history or [], max_turns=10)

    # Contextual background injection
    background_notes = []
    if mood_context:
        background_notes.append(f"User Recent Check-in: {mood_context}")
    if stress_level is not None:
        background_notes.append(f"User Current Stress Score: {stress_level}/10")
    if journal_summary:
        background_notes.append(f"User Recent Journal Reflection: {journal_summary}")

    system_prompt = WELLNESS_SYSTEM_PROMPT
    if background_notes:
        system_prompt += "\n\n[USER WELLNESS CONTEXT]\n" + "\n".join(background_notes)

    # Always reload .env so updates to keys or models are immediately active
    load_dotenv(override=True)

    # Build prioritized list of available external AI providers
    available_providers = []
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        available_providers.append("gemini")
    if os.getenv("GROQ_API_KEY"):
        available_providers.append("groq")
    if os.getenv("OPENAI_API_KEY"):
        available_providers.append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        available_providers.append("anthropic")

    if not available_providers:
        logger.warning("No External AI API Key configured in .env.")
        return (
            "I hear you, and thank you for sharing that with me. "
            "Take a slow, deep breath in... and gently release it.\n\n"
            "*(Note: To enable live responses from Google Gemini, Groq, or OpenAI, please set your API key in the `.env` file.)*"
        )

    # Attempt providers in cascade order to ensure 100% resilience against transient 404/quota errors
    last_error_summary = None
    for prov in available_providers:
        try:
            if prov == "gemini":
                return _call_gemini_api(clean_user_message, trimmed_history, system_prompt)
            elif prov in ("openai", "groq"):
                return _call_openai_compatible_api(clean_user_message, trimmed_history, system_prompt, provider=prov)
            elif prov == "anthropic":
                return _call_anthropic_api(clean_user_message, trimmed_history, system_prompt)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            logger.warning(f"External AI API HTTP error ({prov}): {e.code} - {error_body}")
            last_error_summary = f"{e.code}"
            continue
        except Exception as e:
            logger.warning(f"External AI API request error ({prov}): {e}")
            last_error_summary = str(e)
            continue

    # Warm, empathetic fallback if all providers encounter temporary network/quota limits
    return (
        "I hear you, and I am right here with you. Take a slow, gentle breath in... and let it out smoothly. "
        "Feel free to share more of what's on your mind—I am listening and here to support you."
    )


# ==============================================================================
# DASHBOARD ROBOT ASSISTANT INTERFACE (PRESERVED & ISOLATED)
# ==============================================================================
def get_companion_response(
    user_message: str,
    mood_context: str = "",
    stress_level: Optional[int] = None,
    journal_summary: str = "",
) -> str:
    """Generates concise, speech-friendly replies specifically for the Dashboard Robot Assistant.

    Isolated from the AI Chat page history to preserve robot assistant behavior.
    """
    clean_msg = (user_message or "").strip()
    if not clean_msg:
        return "Hello! I'm your AI Wellness Companion. How are you feeling today?"

    if _contains_crisis_language(clean_msg):
        return CRISIS_RESPONSE

    load_dotenv(override=True)
    available_providers = []
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        available_providers.append("gemini")
    if os.getenv("GROQ_API_KEY"):
        available_providers.append("groq")
    if os.getenv("OPENAI_API_KEY"):
        available_providers.append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        available_providers.append("anthropic")

    if available_providers:
        companion_system = (
            "You are a friendly, encouraging AI Robot Wellness Companion displayed on the user's dashboard. "
            "Give very concise (1 to 3 sentences max), warm, conversational answers suitable for text-to-speech. "
            "Be positive, empathetic, and offer quick calming guidance."
        )
        for prov in available_providers:
            try:
                if prov == "gemini":
                    return _call_gemini_api(clean_msg, [], companion_system)
                elif prov in ("openai", "groq"):
                    return _call_openai_compatible_api(clean_msg, [], companion_system, provider=prov)
                elif prov == "anthropic":
                    return _call_anthropic_api(clean_msg, [], companion_system)
            except Exception as e:
                logger.warning(f"Companion external API fallback ({prov}): {e}")
                continue

    # Fallback response for dashboard robot companion
    lowered = clean_msg.lower()
    if "stress" in lowered or "anxious" in lowered:
        return "I hear you. Let's take a slow breath together: inhale for 4 seconds, and exhale gently."
    elif "happy" in lowered or "great" in lowered or "good" in lowered:
        return "That's wonderful to hear! Savor this positive headspace today."
    elif "sad" in lowered or "tired" in lowered or "exhausted" in lowered:
        return "I'm right here with you. Remember that resting is productive too. Be kind to yourself today."
    return "I'm right here with you. Take a slow, calm breath, and take things one step at a time."


# ==============================================================================
# CONVERSATION TITLE GENERATOR (FAST & LOCAL)
# ==============================================================================
# Backward-compatibility alias
get_chat_response = get_external_ai_chat_response


def generate_chat_title(user_message: str) -> str:

    """Generates a concise, meaningful conversation title from the first message."""
    clean_text = (user_message or "").strip()
    if not clean_text:
        return "New Reflection"

    lowered = clean_text.lower()
    greeting_words = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening"}
    if lowered in greeting_words or any(lowered.startswith(w) for w in greeting_words):
        return "Initial Reflection"

    if any(k in lowered for k in ("exam", "test", "study", "college", "school")):
        return "Academic Reflection"
    elif any(k in lowered for k in ("work", "job", "career", "boss", "office")):
        return "Workplace Reflection"
    elif any(k in lowered for k in ("sleep", "rest", "tired", "insomnia")):
        return "Rest & Sleep Log"
    elif any(k in lowered for k in ("lonely", "alone", "friend", "relationship")):
        return "Emotional Check-In"
    elif any(k in lowered for k in ("stress", "anxious", "worry", "panic", "overwhelmed")):
        return "Stress Management"

    words = [w for w in re.findall(r"\b\w+\b", clean_text) if len(w) > 2]
    stopwords = {"the", "and", "that", "this", "with", "from", "have", "been", "feel", "feeling", "really", "very", "just", "what", "about"}
    filtered_words = [w.capitalize() for w in words if w.lower() not in stopwords]

    if len(filtered_words) >= 2:
        return " ".join(filtered_words[:3])[:30].title()
    elif len(filtered_words) == 1:
        return f"{filtered_words[0]} Reflection"

    return "Daily Reflection"
