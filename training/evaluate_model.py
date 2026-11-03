"""Evaluation script for the Emotion Classification model.

Loads the trained model from models/ and evaluates performance against test data,
printing Accuracy, Precision, Recall, F1 Scores, and saving detailed evaluation reports.
"""
import os
import json
import logging
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def evaluate_saved_model(test_csv_path: str = None):
    """Evaluate the trained model on a target test CSV or dataset."""
    model_path = config.MODEL_SAVE_PATH
    if not os.path.exists(model_path):
        logger.error(f"Model file not found at {model_path}. Please run train_emotion_model.py first.")
        return None

    logger.info(f"Loading trained model from {model_path}...")
    payload = joblib.load(model_path)
    vectorizer = payload["vectorizer"]
    classifier = payload["classifier"]
    emotions = payload["emotions"]

    if test_csv_path is None:
        test_csv_path = os.path.join(config.PROCESSED_DATA_DIR, "processed_emotions.csv")

    if not os.path.exists(test_csv_path):
        logger.error(f"Test dataset not found at {test_csv_path}.")
        return None

    df = pd.read_csv(test_csv_path)
    df = df.dropna(subset=["text", "emotion"])
    df = df[df["emotion"].isin(emotions)]

    logger.info(f"Evaluating model on {len(df)} samples from {test_csv_path}...")

    X_vec = vectorizer.transform(df["text"].tolist())
    y_true = np.array(df["emotion"].tolist(), dtype=object)


    y_pred = classifier.predict(X_vec)
    y_prob = classifier.predict_proba(X_vec)

    acc = accuracy_score(y_true, y_pred)
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted")
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro")

    report_str = classification_report(y_true, y_pred, target_names=emotions, zero_division=0)

    logger.info("\n" + "=" * 50)
    logger.info("EVALUATION RESULTS SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Accuracy:           {acc:.4f} ({acc * 100:.2f}%)")
    logger.info(f"Weighted Precision: {weighted_p:.4f}")
    logger.info(f"Weighted Recall:    {weighted_r:.4f}")
    logger.info(f"Weighted F1-Score:  {weighted_f1:.4f}")
    logger.info(f"Macro F1-Score:     {macro_f1:.4f}")
    logger.info("=" * 50)
    logger.info("\nClassification Report:\n" + report_str)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=emotions)
    plt.figure(figsize=(9, 7))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Purples",
        xticklabels=emotions,
        yticklabels=emotions,
    )
    plt.title("Evaluated Emotion Classifier - Confusion Matrix")
    plt.xlabel("Predicted Emotion")
    plt.ylabel("True Emotion")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    os.makedirs(config.EVALUATION_DIR, exist_ok=True)
    eval_cm_path = config.EVALUATION_CM_PATH
    training_eval_cm = os.path.join(config.TRAINING_DIR, "eval_confusion_matrix.png")
    plt.savefig(eval_cm_path, dpi=300)
    plt.savefig(training_eval_cm, dpi=300)
    plt.close()
    logger.info(f"Saved evaluation confusion matrix to {eval_cm_path}")

    res = {
        "accuracy": float(acc),
        "weighted_precision": float(weighted_p),
        "weighted_recall": float(weighted_r),
        "weighted_f1": float(weighted_f1),
        "macro_precision": float(macro_p),
        "macro_recall": float(macro_r),
        "macro_f1": float(macro_f1),
        "total_samples": int(len(df)),
    }

    report_path = config.EVALUATION_REPORT_PATH
    training_report_path = os.path.join(config.TRAINING_DIR, "evaluation_report.json")
    with open(report_path, "w") as f:
        json.dump(res, f, indent=2)
    with open(training_report_path, "w") as f:
        json.dump(res, f, indent=2)

    return res


if __name__ == "__main__":
    evaluate_saved_model()

