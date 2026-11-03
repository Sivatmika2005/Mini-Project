"""Dataset preparation module for AI Wellness Chatbot Emotion Classifier.

Parses GoEmotions dataset, maps labels to target 7 wellness classes, cleans text while preserving negations, balances classes, and exports processed dataset.
"""
import os
import re
import json
import logging
import pandas as pd
import numpy as np
from typing import Tuple

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Clean and normalize raw input text while preserving negation words."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[NAME\]|\[RELIGION\]", "", text)
    # Expand common contractions so negations are preserved distinctly
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"'re", " are", text)
    text = re.sub(r"'s", " is", text)
    text = re.sub(r"'d", " would", text)
    text = re.sub(r"'ll", " will", text)
    text = re.sub(r"'ve", " have", text)
    text = re.sub(r"'m", " am", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_goemotions(filepath: str = None) -> pd.DataFrame:
    """Load and process Google GoEmotions dataset."""
    if filepath is None:
        filepath = os.path.join(config.DATASETS_DIR, "goemotions.csv")

    if not os.path.exists(filepath):
        logger.warning(f"GoEmotions file not found at {filepath}")
        return pd.DataFrame(columns=["text", "emotion"])

    logger.info(f"Loading GoEmotions dataset from {filepath}...")
    df = pd.read_csv(filepath)

    if "text" not in df.columns:
        logger.error("Invalid GoEmotions format: missing 'text' column.")
        return pd.DataFrame(columns=["text", "emotion"])

    records = []
    emotion_cols = [col for col in config.GOEMOTIONS_MAP.keys() if col in df.columns]

    for idx, row in df.iterrows():
        text = clean_text(row["text"])
        if not text or len(text) < 3:
            continue

        active_emotions = [col for col in emotion_cols if row[col] == 1]
        for emo in active_emotions:
            target_emo = config.GOEMOTIONS_MAP.get(emo)
            if target_emo:
                records.append({"text": text, "emotion": target_emo, "source": "goemotions"})

    res_df = pd.DataFrame(records)
    logger.info(f"Processed GoEmotions: {len(res_df)} mapped samples.")
    return res_df


def load_dair_emotion(filepath: str = None) -> pd.DataFrame:
    """Load and process DAIR Emotion dataset (dair-ai/emotion)."""
    if filepath is None:
        filepath = os.path.join(config.DATASETS_DIR, "dair_emotion.csv")

    if not os.path.exists(filepath):
        logger.info(f"DAIR Emotion dataset file not found at {filepath}, skipping local load.")
        return pd.DataFrame(columns=["text", "emotion"])

    logger.info(f"Loading DAIR Emotion dataset from {filepath}...")
    df = pd.read_csv(filepath)

    text_col = "text" if "text" in df.columns else df.columns[0]
    label_col = "label" if "label" in df.columns else df.columns[1]

    records = []
    for _, row in df.iterrows():
        text = clean_text(row[text_col])
        raw_label = str(row[label_col]).lower()
        mapped_label = config.DAIR_EMOTION_MAP.get(raw_label)
        if text and mapped_label:
            records.append({"text": text, "emotion": mapped_label, "source": "dair_emotion"})

    res_df = pd.DataFrame(records)
    logger.info(f"Processed DAIR Emotion: {len(res_df)} mapped samples.")
    return res_df


def load_empathetic_dialogues(filepath: str = None) -> pd.DataFrame:
    """Load and process Empathetic Dialogues dataset."""
    if filepath is None:
        filepath = os.path.join(config.DATASETS_DIR, "empathetic_dialogues.csv")

    if not os.path.exists(filepath):
        logger.info(f"Empathetic Dialogues dataset file not found at {filepath}, skipping local load.")
        return pd.DataFrame(columns=["text", "emotion"])

    logger.info(f"Loading Empathetic Dialogues from {filepath}...")
    df = pd.read_csv(filepath)

    text_col = "utterance" if "utterance" in df.columns else ("text" if "text" in df.columns else df.columns[0])
    label_col = "context" if "context" in df.columns else ("emotion" if "emotion" in df.columns else df.columns[1])

    records = []
    for _, row in df.iterrows():
        text = clean_text(row[text_col])
        raw_label = str(row[label_col]).lower()
        mapped_label = config.EMPATHETIC_DIALOGUES_MAP.get(raw_label)
        if text and mapped_label:
            records.append({"text": text, "emotion": mapped_label, "source": "empathetic_dialogues"})

    res_df = pd.DataFrame(records)
    logger.info(f"Processed Empathetic Dialogues: {len(res_df)} mapped samples.")
    return res_df


def get_synthetic_wellness_dataset() -> pd.DataFrame:
    """High quality contextual emotion dataset including explicit sentence negations and conversational dialogues."""
    seed_data = [
        # Happy / Recovery / Accomplishments
        ("happy", "Happy"),
        ("I feel happy", "Happy"),
        ("I am happy", "Happy"),
        ("I feel good", "Happy"),
        ("I feel great", "Happy"),
        ("I am feeling happy today", "Happy"),
        ("I had a wonderful day", "Happy"),
        ("I feel wonderful today", "Happy"),
        ("I am so happy and joyful", "Happy"),
        ("Today was a wonderful day", "Happy"),
        ("I am feeling great and happy", "Happy"),
        ("not bad", "Happy"),
        ("feeling not bad", "Happy"),
        ("not sad", "Happy"),
        ("I am not sad", "Happy"),
        ("I am not sad anymore", "Happy"),
        ("I'm no longer sad", "Happy"),
        ("no longer sad", "Happy"),
        ("not lonely", "Happy"),
        ("I don't feel lonely anymore", "Happy"),
        ("no longer lonely", "Happy"),
        ("not stressed anymore", "Happy"),
        ("I'm not stressed anymore", "Happy"),
        ("I passed my exam", "Happy"),
        ("I passed my test", "Happy"),
        ("I passed my exam today", "Happy"),
        ("I did great on my exam", "Happy"),
        ("I got the job", "Happy"),
        ("I got promoted", "Happy"),
        ("I got into my dream college", "Happy"),

        # Sad / Distress / Negated Positives
        ("sad", "Sad"),
        ("I feel sad", "Sad"),
        ("I am sad", "Sad"),
        ("not happy", "Sad"),
        ("I am not happy", "Sad"),
        ("I am not happy at all", "Sad"),
        ("I don't feel happy", "Sad"),
        ("not good", "Sad"),
        ("I don't feel good", "Sad"),
        ("not fine", "Sad"),
        ("I'm not fine", "Sad"),
        ("not okay", "Sad"),
        ("I'm not okay today", "Sad"),
        ("I don't know why I am crying", "Sad"),
        ("I feel empty", "Sad"),
        ("lonely", "Sad"),
        ("I feel lonely", "Sad"),
        ("alone", "Sad"),
        ("i am alone", "Sad"),
        ("feeling alone", "Sad"),
        ("dull", "Sad"),
        ("feeling dull", "Sad"),
        ("depressed", "Sad"),
        ("I feel lonely and isolated", "Sad"),
        ("I feel so alone in the world", "Sad"),
        ("I am feeling sad and depressed", "Sad"),
        ("I failed my exam", "Sad"),
        ("I lost my job", "Sad"),
        ("I lost my wallet", "Sad"),

        # Stress
        ("I'm stressed", "Stress"),
        ("I am stressed", "Stress"),
        ("I feel so stressed out", "Stress"),
        ("I feel stressed about work", "Stress"),
        ("I couldn't sleep", "Stress"),
        ("I could not sleep last night", "Stress"),
        ("I couldn't sleep because of stress", "Stress"),
        ("Too much work and stress", "Stress"),
        ("I am feeling stressed and overwhelmed", "Stress"),

        # Excited
        ("I am excited", "Excited"),
        ("I feel excited", "Excited"),
        ("I am so excited for the weekend", "Excited"),
        ("I feel excited about the future", "Excited"),
        ("I am thrilled and excited", "Excited"),
        ("I am excited but also nervous", "Excited"),

        # Anxiety
        ("I feel anxious", "Anxiety"),
        ("I am anxious", "Anxiety"),
        ("I'm scared", "Anxiety"),
        ("I am scared", "Anxiety"),
        ("I'm worried about tomorrow's exam", "Anxiety"),
        ("I am worried about my presentation", "Anxiety"),
        ("I have severe anxiety about tomorrow", "Anxiety"),
        ("I am feeling very anxious and worried", "Anxiety"),
        ("My mind is racing with anxiety", "Anxiety"),

        # Angry
        ("I am angry", "Angry"),
        ("I feel angry", "Angry"),
        ("I feel so mad and angry", "Angry"),
        ("I am furious about this", "Angry"),

        # Neutral / Conversational Greetings & Transitions
        ("hello", "Neutral"),
        ("hi", "Neutral"),
        ("hey", "Neutral"),
        ("hello there", "Neutral"),
        ("good morning", "Neutral"),
        ("good afternoon", "Neutral"),
        ("good evening", "Neutral"),
        ("how are you", "Neutral"),
        ("how are you doing", "Neutral"),
        ("how is it going", "Neutral"),
        ("thank you", "Neutral"),
        ("thanks", "Neutral"),
        ("thank you so much", "Neutral"),
        ("bye", "Neutral"),
        ("goodbye", "Neutral"),
        ("okay", "Neutral"),
        ("fine", "Neutral"),
        ("good", "Neutral"),
        ("I feel okay now", "Neutral"),
        ("I am fine", "Neutral"),
        ("I feel fine", "Neutral"),
        ("I am okay", "Neutral"),
        ("I am sitting at my desk", "Neutral"),
        ("The sky is blue today", "Neutral"),
        ("I ate lunch at noon", "Neutral"),
        ("Just going through my daily tasks", "Neutral"),
        ("I don't know what I'm feeling", "Neutral"),
        ("I am not anxious", "Neutral"),
        ("I feel no anxiety today", "Neutral"),
        ("I am not stressed", "Neutral"),
        ("I am not feeling stressed today", "Neutral"),
        ("I am not angry", "Neutral"),
    ]
    multiplied_seed = seed_data * 50
    records = [{"text": clean_text(t), "emotion": e, "source": "wellness_seeds"} for t, e in multiplied_seed]
    return pd.DataFrame(records)




def balance_dataset(df: pd.DataFrame, target_per_class: int = 2500) -> pd.DataFrame:
    """Resample dataset so every emotion class has balanced representation."""
    balanced_dfs = []
    for emo in config.EMOTIONS:
        sub_df = df[df["emotion"] == emo]
        if len(sub_df) == 0:
            continue
        if len(sub_df) >= target_per_class:
            sub_sampled = sub_df.sample(n=target_per_class, random_state=config.RANDOM_SEED)
        else:
            sub_sampled = sub_df.sample(n=target_per_class, replace=True, random_state=config.RANDOM_SEED)
        balanced_dfs.append(sub_sampled)

    res = pd.concat(balanced_dfs, ignore_index=True).sample(frac=1.0, random_state=config.RANDOM_SEED).reset_index(drop=True)
    return res


def prepare_combined_dataset() -> pd.DataFrame:
    """Load, combine, map, clean, and balance datasets across all 7 target emotion classes."""
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)

    dfs = [
        load_goemotions(),
        load_dair_emotion(),
        load_empathetic_dialogues(),
        get_synthetic_wellness_dataset(),
    ]

    combined = pd.concat([d for d in dfs if not d.empty], ignore_index=True)
    combined.drop_duplicates(subset=["text"], inplace=True)
    combined = combined[combined["emotion"].isin(config.EMOTIONS)].reset_index(drop=True)

    logger.info("Raw Dataset Emotion Breakdown:")
    logger.info(combined["emotion"].value_counts().to_string())

    # Balance classes to 2,500 samples per emotion class (Total = 17,500 samples)
    balanced = balance_dataset(combined, target_per_class=2500)
    logger.info("Balanced Dataset Emotion Breakdown:")
    logger.info(balanced["emotion"].value_counts().to_string())

    out_file = os.path.join(config.PROCESSED_DATA_DIR, "processed_emotions.csv")
    balanced.to_csv(out_file, index=False)
    logger.info(f"Saved balanced dataset ({len(balanced)} samples) to {out_file}")

    return balanced


if __name__ == "__main__":
    prepare_combined_dataset()
