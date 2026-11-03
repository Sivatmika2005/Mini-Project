"""Dataset Preparation Module for LLM Supervised Fine-Tuning (SFT).

Converts processed emotion classification data (CSV) into Hugging Face Chat-formatted JSONL
records containing system instructions, user prompts, and empathetic AI wellness responses.
"""
import os
import sys
import json
import random
import logging
import pandas as pd
from typing import Dict, List, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "training", "data", "processed_emotions.csv")
JSONL_OUTPUT_PATH = os.path.join(BASE_DIR, "training", "data", "mental_health_sft.jsonl")

SYSTEM_PROMPT = (
    "You are a warm, empathetic AI mental wellness companion. "
    "Provide supportive, non-judgmental, and practical guidance for emotional well-being, "
    "mindfulness, stress management, and personal reflection."
)

# Empathetic Response Generators mapped to target wellness emotions
EMPATHETIC_RESPONSES: Dict[str, List[str]] = {
    "Happy": [
        "It's wonderful to hear that you're feeling positive! Celebrating joyful moments builds lasting resilience. What has been the best part of your day?",
        "I'm so glad to hear that! Taking a moment to appreciate good news or a bright mood is a great practice. How are you sharing or holding onto this joy today?",
        "That is great news! Experiencing happiness and satisfaction is something to cherish. What brightened your spirit today?",
        "Hearing about your positive mood brings warmth! Keep nurturing those feelings—what is one thing you are grateful for right now?"
    ],
    "Sad": [
        "I hear how much sadness is in your words, and I want you to know that your feelings are completely valid. Give yourself permission to take things gently today.",
        "Thank you for sharing your heart with me. Sadness can feel so heavy and exhausting. Would you like to share more about what's causing this feeling, or just sit quietly for a moment?",
        "I'm really sorry things feel so tough right now. Please remember to be gentle with yourself. You don't have to carry this distress all alone—I'm right here with you.",
        "It takes courage to express feeling down. Take a slow, comforting breath. What feels heaviest for you at this moment?"
    ],
    "Anxiety": [
        "I hear the anxiety in what you're sharing. Anxiety can make thoughts feel urgent and overwhelming, but you are safe right now. Let's take a slow inhale for 4 seconds, and exhale for 6 seconds together.",
        "Feeling anxious or worried is really uncomfortable, but remember that this feeling is temporary and will pass. What is one small thing in your room right now that you can focus on to ground yourself?",
        "I understand how unsettling anxiety can feel. Unclench your jaw, drop your shoulders, and take a gentle breath. What feels most uncertain or urgent to you right now?",
        "When worry takes over, focusing on the present moment can help. Name 3 things you can see around you right now—let's take things one moment at a time."
    ],
    "Stress": [
        "I can tell you're carrying a lot of stress right now. When pressure builds up, giving yourself even a 2-minute pause can make a difference. Have you taken a break or had a drink of water recently?",
        "Managing high stress is exhausting. Try to step back from what's pressing on you for a quick moment: stretch your arms, unclench your shoulders, and take a deep breath. Which task can we set aside for later?",
        "It sounds like you have a heavy load on your shoulders. Remember that you don't have to finish everything at once. What is the single most important thing you can tackle first?",
        "When overwhelmed by stress, writing down your thoughts can help unload your mind. Would a quick grounding exercise or box breathing break feel helpful right now?"
    ],
    "Angry": [
        "It sounds like you're dealing with a lot of frustration and anger right now. Anger is a natural, valid response when boundaries or expectations are broken. Take a slow breath—I'm here to listen if you want to express what happened.",
        "I hear how intense this frustration is for you. Expressing anger safely is important. Take a moment to let out a deep exhale—what triggered this strong feeling today?",
        "It is completely understandable to feel angry when things go wrong or feel unfair. Take your time—would you like to vent about what happened, or focus on cooling down first?",
        "Anger signals that something important to you was affected. I'm right here without judgment. What felt most frustrating about this situation?"
    ],
    "Excited": [
        "That sounds incredibly exciting! Energy and enthusiasm are so refreshing. Tell me more about what's coming up!",
        "How wonderful! Feeling excited and energized is fantastic. What are you most looking forward to with this?",
        "Love that positive energy! Celebrating milestones and exciting events gives us so much fuel. How do you plan to enjoy this moment?"
    ],
    "Neutral": [
        "I'm listening and right here with you. How has your day been unfolding so far?",
        "Thank you for connecting today! Being in a steady, reflective space is a good place to pause. What's on your mind today?",
        "I'm right here whenever you'd like to reflect, share a thought, or talk through your day."
    ]
}


def generate_response(text: str, emotion: str) -> str:
    """Selects or customizes an empathetic AI wellness response based on text and emotion."""
    responses = EMPATHETIC_RESPONSES.get(emotion, EMPATHETIC_RESPONSES["Neutral"])
    
    # Specific contextual overrides for common phrases
    text_lower = text.lower()
    if "exam" in text_lower or "test" in text_lower:
        if emotion == "Sad" or emotion == "Stress":
            return "I know how stressful and discouraging exams can feel. Remember that one test result does not define your intelligence or worth. Take a deep breath—how are you holding up right now?"
        elif emotion == "Anxiety":
            return "Exam anxiety is very real, but you've prepared and done your best to get here. Take 3 deep breaths before reviewing anything else—you've got this."
    elif "sleep" in text_lower or "insomnia" in text_lower:
        return "Struggling to sleep can be really frustrating. Try dimming your lights, putting away screens, and trying 4-7-8 breathing (inhale 4s, hold 7s, exhale 8s). Rest softly tonight."
    elif "job" in text_lower or "work" in text_lower:
        if emotion == "Sad" or emotion == "Stress":
            return "Work challenges and job setbacks can feel so heavy. Give yourself grace to process this transition. What is one small step of self-care you can take today?"

    return random.choice(responses)


def validate_record(record: Dict[str, Any]) -> bool:
    """Validates Hugging Face chat-format JSONL structure and content."""
    if not isinstance(record, dict):
        return False
    messages = record.get("messages")
    if not isinstance(messages, list) or len(messages) != 3:
        return False

    roles = [m.get("role") for m in messages]
    if roles != ["system", "user", "assistant"]:
        return False

    user_content = messages[1].get("content", "").strip()
    assistant_content = messages[2].get("content", "").strip()

    if not user_content or not assistant_content:
        return False
    return True


def prepare_sft_dataset():
    """Converts emotion CSV dataset to validated Hugging Face Chat JSONL format."""
    if not os.path.exists(CSV_PATH):
        logger.error(f"Input CSV file not found at: {CSV_PATH}")
        return

    logger.info(f"Reading input dataset from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)

    if "text" not in df.columns or "emotion" not in df.columns:
        logger.error("Dataset missing required 'text' or 'emotion' columns.")
        return

    records = []
    valid_count = 0
    invalid_count = 0
    emotion_stats = {}

    random.seed(42)

    for idx, row in df.iterrows():
        user_text = str(row["text"]).strip()
        emotion = str(row["emotion"]).strip()
        source = str(row.get("source", "wellness_sft")).strip()

        if not user_text or not emotion:
            invalid_count += 1
            continue

        assistant_reply = generate_response(user_text, emotion)

        record = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": assistant_reply},
            ],
            "metadata": {
                "emotion": emotion,
                "source": source,
                "id": idx + 1
            }
        }

        if validate_record(record):
            records.append(record)
            valid_count += 1
            emotion_stats[emotion] = emotion_stats.get(emotion, 0) + 1
        else:
            invalid_count += 1

    os.makedirs(os.path.dirname(JSONL_OUTPUT_PATH), exist_ok=True)
    logger.info(f"Writing {len(records)} validated JSONL records to {JSONL_OUTPUT_PATH}...")

    with open(JSONL_OUTPUT_PATH, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    logger.info("Dataset preparation complete!")
    print("\n" + "=" * 60)
    print("📊 MENTAL HEALTH SFT DATASET STATISTICS")
    print("=" * 60)
    print(f"Total Input Rows Read  : {len(df)}")
    print(f"Valid JSONL Records    : {valid_count}")
    print(f"Invalid / Skipped Rows : {invalid_count}")
    print(f"Output File Path       : {JSONL_OUTPUT_PATH}")
    print("\nBreakdown by Emotion Metadata:")
    for emo, count in sorted(emotion_stats.items()):
        print(f"  - {emo:<10}: {count} records")

    print("\n" + "=" * 60)
    print("📝 SAMPLE SFT CHAT RECORDS (FIRST 3 RECS)")
    print("=" * 60)
    for sample in records[:3]:
        print(json.dumps(sample, indent=2, ensure_ascii=False))
        print("-" * 60)


if __name__ == "__main__":
    prepare_sft_dataset()
