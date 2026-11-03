"""Configuration constants and dataset label mappings for Emotion Classification."""
import os

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(os.path.dirname(BASE_DIR), "datasets")
TRAINING_DIR = os.path.join(BASE_DIR, "training")
MODELS_DIR = os.path.join(BASE_DIR, "models")
EVALUATION_DIR = os.path.join(BASE_DIR, "evaluation")
PROCESSED_DATA_DIR = os.path.join(TRAINING_DIR, "data")

MODEL_SAVE_PATH = os.path.join(MODELS_DIR, "emotion_classifier.joblib")
METADATA_SAVE_PATH = os.path.join(MODELS_DIR, "metadata.json")
CONFUSION_MATRIX_PATH = os.path.join(MODELS_DIR, "confusion_matrix.png")
TRAINING_PLOT_PATH = os.path.join(MODELS_DIR, "training_loss.png")

# Evaluation output paths
EVALUATION_METRICS_PATH = os.path.join(EVALUATION_DIR, "metrics.json")
EVALUATION_REPORT_PATH = os.path.join(EVALUATION_DIR, "evaluation_report.json")
EVALUATION_CM_PATH = os.path.join(EVALUATION_DIR, "confusion_matrix.png")
EVALUATION_LOSS_PATH = os.path.join(EVALUATION_DIR, "training_loss.png")

# Target 7 core wellness classes
EMOTIONS = [
    "Happy",
    "Sad",
    "Anxiety",
    "Stress",
    "Angry",
    "Excited",
    "Neutral",
]

# Map GoEmotions fine-grained labels -> 7 wellness classes
GOEMOTIONS_MAP = {
    "admiration": "Happy",
    "amusement": "Happy",
    "approval": "Happy",
    "caring": "Happy",
    "desire": "Happy",
    "excitement": "Excited",
    "gratitude": "Happy",
    "joy": "Happy",
    "love": "Happy",
    "optimism": "Happy",
    "pride": "Happy",
    "relief": "Happy",
    "surprise": "Excited",
    "anger": "Angry",
    "annoyance": "Stress",
    "disapproval": "Angry",
    "disgust": "Angry",
    "fear": "Anxiety",
    "nervousness": "Anxiety",
    "sadness": "Sad",
    "disappointment": "Sad",
    "grief": "Sad",
    "remorse": "Sad",
    "embarrassment": "Stress",
    "confusion": "Neutral",
    "curiosity": "Neutral",
    "realization": "Neutral",
    "neutral": "Neutral",
}

# Map DAIR Emotion dataset labels -> 7 wellness classes
DAIR_EMOTION_MAP = {
    "joy": "Happy",
    "sadness": "Sad",
    "anger": "Angry",
    "fear": "Anxiety",
    "love": "Happy",
    "surprise": "Excited",
}

# Map Empathetic Dialogues labels -> 7 wellness classes
EMPATHETIC_DIALOGUES_MAP = {
    "afraid": "Anxiety",
    "angry": "Angry",
    "anxious": "Anxiety",
    "apprehensive": "Anxiety",
    "ashamed": "Stress",
    "caring": "Happy",
    "confident": "Happy",
    "content": "Happy",
    "devastated": "Sad",
    "disappointed": "Sad",
    "disgusted": "Angry",
    "embarrassed": "Stress",
    "excited": "Excited",
    "faithful": "Happy",
    "fearful": "Anxiety",
    "furious": "Angry",
    "grateful": "Happy",
    "guilty": "Sad",
    "hopeful": "Happy",
    "impressive": "Happy",
    "jealous": "Stress",
    "joyful": "Happy",
    "lonely": "Sad",
    "nostalgic": "Neutral",
    "prepared": "Neutral",
    "proud": "Happy",
    "resentful": "Angry",
    "sad": "Sad",
    "sentimental": "Neutral",
    "surprised": "Excited",
    "terrified": "Anxiety",
    "trusting": "Happy",
}

# Training Hyperparameters
RANDOM_SEED = 42
TEST_SIZE = 0.15
VAL_SIZE = 0.15
MAX_FEATURES = 20000
NGRAM_RANGE = (1, 3)
C_PARAM = 2.0
MAX_ITER = 1000

