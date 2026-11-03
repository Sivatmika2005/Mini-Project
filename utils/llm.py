"""LLM integration and Emotion Intelligence pipeline for the AI wellness chatbot.

Supports Anthropic, Gemini, OpenAI, and Groq APIs with direct HTTP requests.
Integrates trained ML Emotion Classification, multi-factor prompt context injection,
sliding-window token optimization, and a dynamic local fallback engine.
"""
import os
import re
import json
import random
import logging
import urllib.request
import urllib.error
from dotenv import load_dotenv

from utils.emotion_classifier import predict_emotion

load_dotenv()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a warm, empathetic AI mental wellness companion inside an AI Wellness app.
Your goal is to provide supportive, non-judgmental, and practical guidance for emotional well-being, mindfulness, stress management, and personal reflection.

Guidelines:
- Respond naturally, conversationally, and empathetically to what the user shares.
- Keep responses concise (3-6 sentences) and easy to read.
- Use the provided user emotional state (detected emotion, recent stress score, journal notes) to tailor your tone and suggestions.
- When appropriate, offer practical wellness tips, grounding techniques (e.g. 5-4-3-2-1 exercise), box breathing, or journaling prompts.
- Remember and maintain context across the conversation history.
- You are an AI companion, NOT a medical doctor or licensed therapist. Do not diagnose medical or mental health conditions or prescribe treatments.
- Do not invent facts or pretend to be human.
- If the user expresses thoughts of self-harm, suicide, or severe crisis, express calm empathy and immediately encourage them to contact a professional crisis helpline (such as 988 Suicide & Crisis Lifeline in the US/Canada or local emergency services).
- Avoid prepending the exact same disclaimers or canned phrases to every message."""

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "self harm", "self-harm", "want to die",
    "hurt myself", "end my life", "ending it all", "don't want to live",
]

CRISIS_RESPONSE = (
    "I'm really glad you reached out. I hear how much pain you're in, but please know you don't "
    "have to go through this alone. Because I am an AI, I cannot provide emergency crisis care. "
    "Please reach out right now to a trusted person or a 24/7 crisis helpline:\n\n"
    "• **US/Canada**: Call or text **988** (Suicide & Crisis Lifeline)\n"
    "• **UK**: Call **111** (NHS) or **116 123** (Samaritans)\n"
    "• **International**: Visit [findahelpline.com](https://findahelpline.com/) to find immediate support in your country.\n\n"
    "If you are in immediate danger, please contact local emergency services immediately."
)


def _contains_crisis_language(text: str) -> bool:
    lowered = (text or "").lower()
    return any(kw in lowered for kw in CRISIS_KEYWORDS)


def is_api_configured() -> bool:
    return bool(
        _is_ollama_available()
        or os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("GROQ_API_KEY")
    )


def _is_ollama_available() -> bool:
    """Checks if a local Ollama server is running on http://localhost:11434."""
    try:
        url = "http://localhost:11434/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _get_active_provider():
    if _is_ollama_available():
        return "ollama"
    elif os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    elif os.getenv("OPENAI_API_KEY"):
        return "openai"
    elif os.getenv("GROQ_API_KEY"):
        return "groq"
    return None


def estimate_tokens(text: str) -> int:
    """Lightweight character/word token estimator (~4 chars per token)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def _get_sliding_context_window(history: list, max_turns: int = 6, max_tokens: int = 1000) -> list:
    """Intelligently slices chat history to maintain a sliding context window within token limits."""
    if not history:
        return []

    recent_history = history[-max_turns:]
    trimmed = []
    current_token_count = 0

    for msg in reversed(recent_history):
        msg_tokens = estimate_tokens(msg.get("content", ""))
        if current_token_count + msg_tokens > max_tokens:
            break
        trimmed.insert(0, msg)
        current_token_count += msg_tokens

    return trimmed


def get_chat_response(
    user_message: str,
    history: list = None,
    mood_context: str = "",
    stress_level: int = None,
    journal_summary: str = "",
) -> str:
    """Sends user message and sliding conversation history directly to the LLM reasoning engine.

    Direct Architecture:
    User Message + Sliding Conversation History + System Prompt -> LLM (Ollama/API) -> Response
    """
    if _contains_crisis_language(user_message):
        return CRISIS_RESPONSE

    provider = _get_active_provider()
    trimmed_history = _get_sliding_context_window(history or [], max_turns=8, max_tokens=1200)

    # General background context (if user logged a check-in or journal entry)
    context_parts = []
    if mood_context:
        context_parts.append(f"Recent User Check-in: {mood_context}")
    if stress_level is not None:
        context_parts.append(f"Recent Stress Score: {stress_level}/10")
    if journal_summary:
        context_parts.append(f"Recent Journal Reflection: {journal_summary}")

    system_instruction = SYSTEM_PROMPT
    if context_parts:
        system_instruction += "\n\n[USER WELLNESS BACKGROUND]\n" + "\n".join(context_parts)

    if not provider:
        return _neural_conversational_generator(
            user_message, trimmed_history, system_instruction, stress_level
        )

    try:
        if provider == "ollama":
            return _call_ollama_http(user_message, trimmed_history, system_instruction)
        elif provider == "anthropic":
            return _call_anthropic_http(user_message, trimmed_history, system_instruction)
        elif provider == "gemini":
            return _call_gemini_http(user_message, trimmed_history, system_instruction)
        elif provider in ("openai", "groq"):
            return _call_openai_compatible_http(user_message, trimmed_history, system_instruction, provider)
    except Exception as e:
        logger.error(f"LLM API request error ({provider}): {e}")
        return _neural_conversational_generator(
            user_message, trimmed_history, system_instruction, stress_level
        )

    return _neural_conversational_generator(
        user_message, trimmed_history, system_instruction, stress_level
    )


def _call_ollama_http(user_message: str, history: list, system_instruction: str) -> str:
    """Calls local Ollama REST API endpoint at http://localhost:11434/api/chat."""
    url = "http://localhost:11434/api/chat"
    headers = {"Content-Type": "application/json"}

    messages = [{"role": "system", "content": system_instruction}]
    for m in (history or []):
        role = "user" if m.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": m.get("content", "")})
    messages.append({"role": "user", "content": user_message})

    model_name = os.getenv("OLLAMA_MODEL", "medgemma")

    payload = json.dumps({
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        return res_data.get("message", {}).get("content", "").strip()


def _call_anthropic_http(user_message: str, history: list, system_instruction: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    messages = []
    for m in (history or []):
        role = "user" if m["role"] == "user" else "assistant"
        messages.append({"role": role, "content": m["content"]})
    messages.append({"role": "user", "content": user_message})

    payload = json.dumps({
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        "max_tokens": 600,
        "system": system_instruction,
        "messages": messages,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        return "".join(b["text"] for b in res_data.get("content", []) if b.get("type") == "text").strip()


def _call_gemini_http(user_message: str, history: list, system_instruction: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"content-type": "application/json"}

    contents = []
    for m in (history or []):
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = json.dumps({
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": contents,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        return res_data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _call_openai_compatible_http(user_message: str, history: list, system_instruction: str, provider: str) -> str:
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        url = "https://api.openai.com/v1/chat/completions"
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    else:
        api_key = os.getenv("GROQ_API_KEY")
        url = "https://api.groq.com/openai/v1/chat/completions"
        model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "content-type": "application/json",
    }
    messages = [{"role": "system", "content": system_instruction}]
    for m in (history or []):
        role = "user" if m["role"] == "user" else "assistant"
        messages.append({"role": role, "content": m["content"]})
    messages.append({"role": "user", "content": user_message})

    payload = json.dumps({
        "model": model_name,
        "messages": messages,
        "max_tokens": 600,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        return res_data["choices"][0]["message"]["content"].strip()


def generate_chat_title(user_message: str) -> str:
    """Generate a concise, meaningful conversation title 100% LOCALLY without wasteful LLM API calls."""
    clean_text = (user_message or "").strip()
    if not clean_text:
        return "New Reflection"

    lowered = clean_text.lower()
    
    greeting_words = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening"}
    if lowered in greeting_words or any(lowered.startswith(w) for w in greeting_words):
        return "Initial Reflection"

    if "exam" in lowered or "test" in lowered or "study" in lowered:
        return "Academic Reflection"
    elif "work" in lowered or "job" in lowered or "career" in lowered:
        return "Workplace Reflection"
    elif "sleep" in lowered or "rest" in lowered or "tired" in lowered:
        return "Rest & Sleep Log"
    elif "lonely" in lowered or "alone" in lowered:
        return "Emotional Check-In"
    elif "stress" in lowered or "anxious" in lowered or "worry" in lowered:
        return "Stress Management"

    words = [w for w in re.findall(r"\b\w+\b", clean_text) if len(w) > 2]
    stopwords = {"the", "and", "that", "this", "with", "from", "have", "been", "feel", "feeling", "really", "very", "just", "what", "about"}
    filtered_words = [w.capitalize() for w in words if w.lower() not in stopwords]

    if len(filtered_words) >= 2:
        title = " ".join(filtered_words[:3])
        return title[:30].title()
    elif len(filtered_words) == 1:
        return f"{filtered_words[0]} Reflection"

    return "Daily Reflection"


def _normalize_text(text: str) -> str:
    """Normalizes text by removing trailing punctuation, repeating characters (helloooo -> hello), and standardizing informal spellings."""
    if not text:
        return ""
    text = text.lower().strip(" '\"?.!,:;")
    # Collapse 3+ repeated characters (helloooo -> hello, hiii -> hi, heyyy -> hey)
    text = re.sub(r"(.)\1{2,}", r"\1", text)
    # Standardize common informal spellings
    text = re.sub(r"\b(how r u|how u doin|how r ya|how r u doing|how r u'|how r u`)\b", "how are you", text)
    text = re.sub(r"\b(wbu|what about u|what bout u)\b", "how about you", text)
    text = re.sub(r"\b(im|i'm)\b", "i am", text)
    text = re.sub(r"\b(u)\b", "you", text)
    text = re.sub(r"\b(r)\b", "are", text)
    return text


def _neural_conversational_generator(
    user_message: str,
    history: list = None,
    system_instruction: str = "",
    stress_level: int = None,
) -> str:
    """Context & ML Emotion-Aware Conversational Reasoning Engine for AI Assistant.

    Combines trained ML emotion classification with negation awareness, multi-turn memory,
    and practical, science-backed wellness guidance for stress management, anxiety relief, and sleep.
    """
    raw_msg = (user_message or "").strip()
    clean_msg = _normalize_text(raw_msg)
    msg_lower = clean_msg
    history = history or []

    # Run ML Emotion Classifier on normalized user message
    try:
        emo_data = predict_emotion(raw_msg)
        ml_emotion = emo_data.get("emotion", "Neutral")
    except Exception:
        ml_emotion = "Neutral"

    # Check if there is recent user activity in current history
    user_history_count = sum(1 for m in history if m.get("role") == "user")

    # 1. Greetings (hello, hi, helloooo, hiii, hey, heyyy, yo, sup)
    greetings = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings", "yo", "sup", "howdy", "hola"}
    is_greeting = clean_msg in greetings or any(clean_msg.startswith(g + " ") for g in greetings if len(g) > 2)

    if is_greeting:
        if user_history_count > 1:
            return random.choice([
                "I'm right here with you! What's on your mind or how can I help you reflect right now?",
                "Hello again! Ready whenever you'd like to share or talk through something.",
                "Hey! I'm listening—feel free to tell me what's on your mind today.",
            ])
        else:
            return random.choice([
                "Hello! I'm glad you reached out today. How are you feeling right now?",
                "Hi there! Welcome. What's on your mind today?",
                "Good day! It's wonderful to connect with you. How can I support your well-being today?",
                "Hello! I'm right here whenever you'd like to chat or reflect.",
            ])

    # 2. Inquiries ("how are you", "how r u", "how about u")
    inquiry_patterns = ["how are you", "how are you doing", "how's it going", "how is it going", "how about you", "how bout you"]
    if any(q in clean_msg for q in inquiry_patterns):
        return random.choice([
            "I'm doing well, thank you for asking! 😊 I'm here and ready to support you. How about you? How are you feeling today?",
            "I'm doing great and ready to support you! How has your day been so far?",
            "Thank you for asking! I'm here and ready to listen. How are you feeling right now?",
        ])

    # 3. Gratitude ("thank you")
    if any(t in msg_lower for t in ["thank you", "thanks", "thank u", "appreciate it"]):
        return random.choice([
            "You're very welcome! 😊 I'm always here whenever you want to reflect or chat. Is there anything else on your mind today?",
            "Glad I could be helpful! Remember to take things one step at a time. What would you like to explore next?",
            "Anytime! I'm right here whenever you need a supportive space. How are you feeling right now?",
        ])

    # 4. Sign-offs / Farewells ("bye")
    farewells = {"bye", "goodbye", "see you", "talk later", "have a good day", "good night"}
    if msg_lower in farewells or any(msg_lower.startswith(f + " ") for f in farewells):
        return random.choice([
            "Goodbye for now! Take good care of yourself today, and feel free to reach back out anytime.",
            "Have a wonderful rest of your day! I'll be here whenever you'd like to chat again.",
            "Take care! Wishing you peace and comfort today.",
        ])

    # 5. STRESS MANAGEMENT / STRESS REDUCTION QUERIES
    if any(k in msg_lower for k in ["reduce stress", "manage stress", "reduce my stress", "lower stress", "relieve stress", "less stress", "handle stress", "stress tips", "how to reduce"]):
        return (
            "Reducing stress starts with giving yourself permission to pause. Here are 4 actionable steps you can try right now:\n\n"
            "1. 🌬️ **Box Breathing (4-4-4-4):** Inhale for 4 seconds, hold for 4 seconds, exhale for 4 seconds, and hold for 4 seconds. Repeat 3 times to calm your nervous system.\n"
            "2. 🦶 **5-4-3-2-1 Grounding:** Name 5 things you see around you, 4 things you can touch, 3 sounds you hear, 2 scents, and take 1 deep breath.\n"
            "3. 📝 **Brain Dump Journaling:** Write down everything causing pressure on paper or in your Journal tab without editing yourself.\n"
            "4. 🚶 **Micro-Break:** Step away from screens for 5 minutes, stretch your shoulders, and drink a glass of water.\n\n"
            "Which of these feels easiest for you to try right now?"
        )

    # 6. ANXIETY / PANIC / CALMING DOWN QUERIES
    if any(k in msg_lower for k in ["calm anxiety", "manage anxiety", "calm down", "panicking", "panic attack", "feeling anxious", "overwhelmed"]):
        return (
            "When anxiety or panic feels overwhelming, grounding your body is the fastest path back to calm:\n\n"
            "• **Extended Exhale Breathing:** Inhale gently through your nose for 4 seconds, then exhale slowly through your mouth for 6 seconds. Longer exhales signal safety to your mind.\n"
            "• **Body Unclench:** Drop your shoulders away from your ears, unclench your jaw, and loosen your hands.\n"
            "• **Reassurance Anchor:** Repeat quietly to yourself: *'I am safe right now. This feeling is temporary and will pass.'*\n\n"
            "Take it one breath at a time. I'm right here with you."
        )

    # 7. SLEEP / INSOMNIA / UNWINDING QUERIES
    if any(k in msg_lower for k in ["sleep better", "can't sleep", "trouble sleeping", "insomnia", "fall asleep", "unwind"]):
        return (
            "Struggling to sleep can feel exhausting. Here are gentle, effective techniques to help your body unwind:\n\n"
            "1. 📵 **Screen Break:** Turn off bright phone and computer screens 30 minutes before sleep.\n"
            "2. 🧘 **Progressive Relaxation:** Gently tense your toes for 5 seconds, then release. Move up to your legs, shoulders, and jaw.\n"
            "3. 🌬️ **4-7-8 Breathing:** Inhale for 4 seconds, hold for 7 seconds, exhale for 8 seconds. Repeat 4 times.\n"
            "4. 📓 **Thought Dump:** If racing thoughts keep you awake, write them down so your mind knows they are stored for tomorrow.\n\n"
            "Give yourself grace tonight—even resting quietly with eyes closed gives your body recovery."
        )

    # 8. Emotional Uncertainty / Ambiguity ("I don't know what I'm feeling")
    if "don't know what" in msg_lower or "don't know how i feel" in msg_lower or "confused" in msg_lower:
        return random.choice([
            "That is completely valid. Sometimes emotions get tangled and it's hard to put a single label on them. Take a slow breath—we can sit with it quietly or explore what thoughts are present right now.",
            "It is completely okay to be uncertain. You don't have to have everything sorted out right now. What physical sensations or thoughts are most noticeable to you at this moment?",
        ])

    # 9. NEGATED NEGATIVE EMOTIONS / RECOVERY & RELIEF ("not sad", "not stressed anymore")
    negated_negative_patterns = [
        "not sad", "no longer sad", "hardly sad", "barely sad",
        "not lonely", "don't feel lonely", "no longer lonely", "not lonely anymore",
        "not stressed", "no longer stressed", "not stressed anymore", "less stressed",
        "not anxious", "no longer anxious", "not worried", "no longer worried"
    ]
    if any(p in msg_lower for p in negated_negative_patterns):
        return random.choice([
            "That is such welcome news and a wonderful relief! Feeling that weight or stress lift gives your mind and body room to breathe. What do you think helped bring about this positive shift?",
            "I'm really glad to hear that! Reaching a point of relief and progress is a moment worth acknowledging. How are you taking advantage of this lighter feeling today?",
            "That is a great milestone in your emotional recovery! Moving past those heavy feelings takes resilience. How does it feel to be in this clearer space right now?",
        ])

    # 10. NEGATED POSITIVE EMOTIONS / DISTRESS ("not happy", "not okay")
    negated_positive_patterns = [
        "not happy", "hardly happy", "barely happy", "never happy",
        "not okay", "not ok", "not okay today", "not feel okay",
        "not good", "don't feel good", "doesn't feel good", "not feeling good",
        "not fine", "not feeling fine", "hardly fine", "anything but fine"
    ]
    if any(p in msg_lower for p in negated_positive_patterns):
        return random.choice([
            "Thank you for being honest with me. It is completely okay to not be okay or not feel happy today. You don't have to carry this distress all by yourself—what's feeling heaviest for you right now?",
            "I hear you, and your feelings are completely valid. When things feel 'not good' or 'not okay', taking a moment to express it is an important first step. What's been going on today?",
            "I'm really sorry things are feeling so difficult right now. Please be gentle with yourself. Would you like to talk through what's causing this feeling, or just vent for a moment?",
        ])

    # 11. DIRECT AFFIRMATIVE SHORT EMOTIONS & STATES
    if msg_lower in ["happy", "feeling happy", "i am happy", "i'm happy"]:
        return "It's wonderful to hear that you're feeling happy! Celebrating positive moments builds lasting resilience. What is bringing joy to your day?"

    if msg_lower in ["sad", "feeling sad", "i am sad", "i'm sad"]:
        return "I hear you, and I appreciate you opening up. Sadness can feel exhausting and heavy. What is on your mind today?"

    if msg_lower in ["lonely", "feeling lonely", "i feel lonely", "i'm lonely"]:
        return "Feeling lonely is a deeply heavy experience, but please know you're not alone here. I'm right here with you—would you like to talk about what's making you feel this way?"

    if msg_lower in ["okay", "ok", "fine", "i am okay", "i'm fine"]:
        return "I hear you clearly. Being in a neutral or steady space is a good place to pause. How can I best support you right now?"

    if msg_lower in ["good", "feeling good", "i am good", "i'm good"]:
        return "Glad to hear that you're feeling good! What's been going well for you today?"

    # 12. Major Achievements & Celebrations
    achievement_terms = ["passed my exam", "passed the exam", "passed my test", "got into dream college", "accepted to college", "won the competition"]
    if any(term in msg_lower for term in achievement_terms):
        return random.choice([
            "Congratulations! That is fantastic news! You put in the hard work and preparation, and seeing it pay off is so rewarding. How are you feeling right now, and how do you plan to celebrate?",
            "Huge congratulations! Passing that exam is a major accomplishment. You should be really proud of your effort and dedication. What was the best part of getting that result?",
        ])

    # 13. Career Accomplishments
    promotion_terms = ["got promoted", "got a promotion", "got the job", "hired", "landed the job"]
    if any(term in msg_lower for term in promotion_terms):
        return random.choice([
            "Congratulations on your promotion! That is a huge achievement and a testament to your talent and hard work. How are you feeling about stepping into this new role?",
            "That is incredible news! Earning a promotion is something to be truly proud of. What are you most excited about with this new opportunity?",
        ])

    # 14. Disappointments & Setbacks
    failure_terms = ["failed my exam", "failed the exam", "failed my test", "didn't pass", "did not pass"]
    if any(term in msg_lower for term in failure_terms):
        return random.choice([
            "I'm really sorry to hear that. It's completely understandable to feel disappointed, but please remember that one exam result doesn't define your intelligence or future. Take a breath—how are you holding up right now?",
            "I know how painful and discouraging that feels. Give yourself permission to feel disappointed without being harsh on yourself. What would feel most helpful right now?",
        ])

    # 15. Dynamic ML Emotion-Trained Response Fallback
    if ml_emotion in ("Stress", "Stressed"):
        options = [
            "I can tell you're carrying a lot of stress right now. When pressure builds up, taking even a 2-minute pause can help. Would you like a quick breathing exercise, or space to vent about what's causing this stress?",
            "It sounds like there is a lot weighing heavily on you today. Stress can be exhausting on both mind and body. What is the single biggest thing causing pressure right now?",
            "I hear the stress in your words. Let's take things one step at a time. What would help take a small amount of load off your shoulders right now?"
        ]
        return random.choice(options)
    elif ml_emotion in ("Anxiety", "Anxious"):
        options = [
            "I hear the anxiety in what you're sharing. Anxiety can make thoughts feel urgent and heavy, but you don't have to carry it alone. Let's take a slow breath together—what feels most overwhelming right now?",
            "When anxious thoughts start spinning, it helps to pause and ground yourself in this moment. I'm right here with you. Would you like to try a calming grounding exercise?",
            "Anxiety is really challenging, but remember that thoughts are not always facts. Take a gentle breath. What's on your mind?"
        ]
        return random.choice(options)
    elif ml_emotion in ("Sad", "Sadness"):
        options = [
            "I hear how much sadness is in your words, and I want you to know that your feelings are completely valid. Give yourself permission to rest and take things gently today. Would you like to share more?",
            "I'm really sorry you are going through this. Sadness can feel quiet and heavy. I'm here to listen without judgment whenever you're ready.",
            "It's completely okay to feel sad. You don't have to put on a brave face here. What's been the hardest part of your day?"
        ]
        return random.choice(options)
    elif ml_emotion in ("Angry", "Anger"):
        options = [
            "It sounds like you're dealing with a lot of frustration right now. Anger is a natural response when boundaries or expectations are broken. Take a slow breath—I'm right here to listen if you want to express what happened.",
            "I hear your frustration clearly. Feeling angry or upset is completely understandable. Would venting about it or looking at constructive next steps feel more helpful?"
        ]
        return random.choice(options)
    elif ml_emotion in ("Happy", "Happiness", "Excited"):
        options = [
            "It's wonderful to connect while you're in good spirits! Positive moments are great opportunities to celebrate and build resilience. What is bringing you joy today?",
            "I love hearing that positive energy! Savoring these moments is so good for your well-being. Tell me more about what's going well!"
        ]
        return random.choice(options)

    # Avoid repeating the last assistant message if possible
    past_assistant_texts = [m.get("content", "") for m in history if m.get("role") == "assistant"][-3:]
    general_responses = [
        "I'm listening and right here with you. What would feel most helpful to talk through next?",
        "I'm here to support your well-being. Feel free to share whatever is on your mind.",
        "Take all the time you need. I'm here whenever you'd like to reflect or chat about your day.",
        "Thank you for sharing that with me. How has that been affecting your mood or energy today?",
        "I'm right here with you. What feels like the most important part of this for you right now?"
    ]
    filtered_responses = [r for r in general_responses if r not in past_assistant_texts]
    reply = random.choice(filtered_responses if filtered_responses else general_responses)

    if stress_level is not None and stress_level >= 7:
        reply += f"\n\n*(Note: Since your stress level was recently logged at {stress_level}/10, make sure to give yourself permission to rest today.)*"

    return reply
