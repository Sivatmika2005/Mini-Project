"""Inference CLI and script for testing the Emotion Classification Model.

Usage:
    python predict.py "I feel so anxious about tomorrow's exam"
"""
import os
import sys
import joblib
import numpy as np

import config

# Add parent directory to sys.path if executed standalone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.emotion_classifier import predict_emotion


def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "I feel really stressed and anxious about all these upcoming deadlines."

    result = predict_emotion(text)

    print("\n" + "=" * 50)
    print("EMOTION PREDICTION RESULT")
    print("=" * 50)
    print(f"Input Text:        \"{text}\"")
    print(f"Predicted Emotion: {result['emotion']}")
    print(f"Confidence Score:  {result['confidence'] * 100:.2f}%")
    print("-" * 50)
    print("Top Probabilities:")
    for emo, prob in list(result["probabilities"].items())[:5]:
        print(f"  - {emo:<12}: {prob * 100:.2f}%")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
