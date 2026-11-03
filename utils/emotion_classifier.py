"""Emotion Classification Inference Module.

Loads trained ML model artifacts from models/ directory and provides high-speed,
calibrated emotion prediction with confidence scores.
"""
import os
import re
import joblib
import logging
import numpy as np
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "emotion_classifier.joblib")

_LOADED_MODEL_PAYLOAD = None
_LAST_LOADED_MTIME = 0


def _load_model():
    global _LOADED_MODEL_PAYLOAD, _LAST_LOADED_MTIME
    if os.path.exists(MODEL_PATH):
        try:
            mtime = os.path.getmtime(MODEL_PATH)
            if _LOADED_MODEL_PAYLOAD is not None and mtime == _LAST_LOADED_MTIME:
                return _LOADED_MODEL_PAYLOAD

            _LOADED_MODEL_PAYLOAD = joblib.load(MODEL_PATH)
            _LAST_LOADED_MTIME = mtime
            logger.info(f"Loaded emotion classification model from {MODEL_PATH} (mtime: {mtime})")
            return _LOADED_MODEL_PAYLOAD
        except Exception as e:
            logger.error(f"Failed to load model from {MODEL_PATH}: {e}")

    return None



def normalize_input_text(text: str) -> str:
    """Normalize input text matching training data preprocessing."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[NAME\]|\[RELIGION\]", "", text)
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


def predict_emotion(text: str) -> Dict[str, Any]:
    """Predict emotion and confidence score using trained ML model.

    Returns:
        dict with keys:
            - emotion: str (e.g. "Sad")
            - confidence: float (0.0 to 1.0)
            - probabilities: dict of {emotion_name: float_probability}
    """
    cleaned_input = normalize_input_text(text)
    if not cleaned_input:
        return {
            "emotion": "Neutral",
            "confidence": 1.0,
            "probabilities": {"Neutral": 1.0},
        }

    payload = _load_model()
    if payload is None:
        raise RuntimeError(
            f"Trained emotion model not found at {MODEL_PATH}. "
            "Please run 'python training/train_emotion_model.py' to generate the model."
        )

    try:
        vectorizer = payload["vectorizer"]
        classifier = payload["classifier"]
        emotions = payload["emotions"]

        vec = vectorizer.transform([cleaned_input])
        probs = classifier.predict_proba(vec)[0]
        top_idx = int(np.argmax(probs))

        predicted_emotion = emotions[top_idx]
        confidence_score = float(np.clip(probs[top_idx], 0.0, 1.0))

        prob_dict = {emotions[i]: float(np.clip(probs[i], 0.0, 1.0)) for i in range(len(emotions))}
        sorted_probs = dict(sorted(prob_dict.items(), key=lambda x: x[1], reverse=True))

        # Console Debug Logging (Task 3 format)
        print("\n" + "=" * 40)
        print(f"User Input: \"{text}\"")
        print("Detected Emotion:")
        print(predicted_emotion)
        print("\nConfidence:")
        print(f"{confidence_score:.2f}")
        print("=" * 40 + "\n")

        logger.info(
            f"ML Prediction: Text='{text}' | Detected Emotion='{predicted_emotion}' | Confidence={confidence_score:.4f}"
        )

        return {
            "emotion": predicted_emotion,
            "confidence": confidence_score,
            "probabilities": sorted_probs,
        }
    except Exception as e:
        logger.error(f"Failed to run inference on trained ML model: {e}")
        raise e


