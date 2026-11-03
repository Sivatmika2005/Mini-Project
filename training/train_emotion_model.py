"""Training pipeline for AI Wellness Chatbot Emotion Classification Model.

Trains TF-IDF + Calibrated Linear Classifier on target 7 wellness classes,
evaluates performance, generates confusion matrix and loss graphs, and exports model artifacts to models/ and evaluation/ directories.
"""
import os
import json
import logging
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
    log_loss,
)

import config
from prepare_dataset import prepare_combined_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def train_and_evaluate():
    """Main training routine."""
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    os.makedirs(config.TRAINING_DIR, exist_ok=True)
    os.makedirs(config.EVALUATION_DIR, exist_ok=True)

    df = prepare_combined_dataset()

    if df.empty:
        logger.error("Dataset is empty! Cannot train model.")
        return

    logger.info(f"Loaded balanced dataset with {len(df)} total samples.")

    df = df.dropna(subset=["text", "emotion"])
    df = df[df["emotion"].isin(config.EMOTIONS)]

    X = np.array(df["text"].tolist(), dtype=object)
    y = np.array(df["emotion"].tolist(), dtype=object)

    # Lexicographically sorted labels
    sorted_classes = np.array(sorted(config.EMOTIONS))


    # Train / Val / Test Split
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_SEED, stratify=y
    )

    val_relative_size = config.VAL_SIZE / (1.0 - config.TEST_SIZE)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_relative_size, random_state=config.RANDOM_SEED, stratify=y_train_val
    )

    logger.info(f"Dataset split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

    # Vectorization with custom negation-aware stopwords
    logger.info("Extracting TF-IDF features...")
    negation_words = {"not", "no", "never", "nor", "neither", "without", "cannot"}
    custom_stopwords = list(set(ENGLISH_STOP_WORDS) - negation_words)

    vectorizer = TfidfVectorizer(
        ngram_range=config.NGRAM_RANGE,
        max_features=config.MAX_FEATURES,
        sublinear_tf=True,
        stop_words=custom_stopwords,
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)
    X_test_vec = vectorizer.transform(X_test)

    # Track SGD loss over epochs for training loss graph
    logger.info("Training SGD loss tracking model for loss curves...")
    sgd_clf = SGDClassifier(
        loss="log_loss",
        penalty="l2",
        alpha=1e-4,
        max_iter=1,
        warm_start=True,
        random_state=config.RANDOM_SEED,
    )

    epochs = 30
    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        perm = np.random.permutation(len(X_train))
        X_tr_shuffled = X_train_vec[perm]
        y_tr_shuffled = y_train[perm]

        sgd_clf.partial_fit(X_tr_shuffled, y_tr_shuffled, classes=sorted_classes)

        train_prob = sgd_clf.predict_proba(X_train_vec)
        val_prob = sgd_clf.predict_proba(X_val_vec)

        tr_loss = log_loss(y_train, train_prob, labels=sorted_classes)
        v_loss = log_loss(y_val, val_prob, labels=sorted_classes)

        train_losses.append(float(tr_loss))
        val_losses.append(float(v_loss))

    # Train Calibrated Classifier (LinearSVC + CalibratedClassifierCV)
    logger.info("Fitting Calibrated Classifier for production inference...")
    base_svc = LinearSVC(C=1.0, random_state=config.RANDOM_SEED, max_iter=2000)
    clf = CalibratedClassifierCV(estimator=base_svc, cv=3)
    clf.fit(X_train_vec, y_train)

    # Evaluate on Test Set
    logger.info("Evaluating model on Test Set...")
    y_pred = clf.predict(X_test_vec)
    y_prob = clf.predict_proba(X_test_vec)

    acc = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted")
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro")

    test_loss = log_loss(y_test, y_prob, labels=clf.classes_)

    report_str = classification_report(y_test, y_pred, labels=clf.classes_, zero_division=0)

    metrics = {
        "accuracy": float(acc),
        "weighted_precision": float(precision),
        "weighted_recall": float(recall),
        "weighted_f1": float(f1),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "test_loss": float(test_loss),
        "train_loss_final": float(train_losses[-1]),
        "val_loss_final": float(val_losses[-1]),
        "train_samples": int(len(X_train)),
        "val_samples": int(len(X_val)),
        "test_samples": int(len(X_test)),
        "emotions": list(clf.classes_),
    }

    logger.info(f"Test Accuracy: {acc:.4f} ({acc * 100:.2f}%)")
    logger.info(f"Test F1-Score (Weighted): {f1:.4f}")
    logger.info("\nClassification Report:\n" + report_str)

    # Generate & Save Confusion Matrix
    cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
    plt.figure(figsize=(9, 7))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=clf.classes_,
        yticklabels=clf.classes_,
    )
    plt.title("Emotion Classifier - Confusion Matrix")
    plt.xlabel("Predicted Emotion")
    plt.ylabel("True Emotion")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    cm_save_path = config.CONFUSION_MATRIX_PATH
    cm_eval_path = config.EVALUATION_CM_PATH
    cm_training_path = os.path.join(config.TRAINING_DIR, "confusion_matrix.png")
    plt.savefig(cm_save_path, dpi=300)
    plt.savefig(cm_eval_path, dpi=300)
    plt.savefig(cm_training_path, dpi=300)
    plt.close()
    logger.info(f"Saved confusion matrix plot to {cm_eval_path}")

    # Generate & Save Training / Validation Loss Curve
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, epochs + 1), train_losses, label="Training Loss", color="#4a90e2", linewidth=2)
    plt.plot(range(1, epochs + 1), val_losses, label="Validation Loss", color="#e74c3c", linewidth=2)
    plt.title("Emotion Classifier - Training vs Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Log Loss")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    loss_save_path = config.TRAINING_PLOT_PATH
    loss_eval_path = config.EVALUATION_LOSS_PATH
    loss_training_path = os.path.join(config.TRAINING_DIR, "training_loss.png")
    plt.savefig(loss_save_path, dpi=300)
    plt.savefig(loss_eval_path, dpi=300)
    plt.savefig(loss_training_path, dpi=300)
    plt.close()
    logger.info(f"Saved training loss curve to {loss_eval_path}")

    # Save Model Artifacts
    model_payload = {
        "vectorizer": vectorizer,
        "classifier": clf,
        "emotions": list(clf.classes_),
    }
    joblib.dump(model_payload, config.MODEL_SAVE_PATH)
    logger.info(f"Saved trained model payload to {config.MODEL_SAVE_PATH}")

    # Save Metadata & Evaluation JSON files inside evaluation/ and models/
    with open(config.METADATA_SAVE_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    with open(config.EVALUATION_METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    eval_report = {
        "metrics": metrics,
        "classification_report": report_str,
    }
    with open(config.EVALUATION_REPORT_PATH, "w") as f:
        json.dump(eval_report, f, indent=2)

    logger.info("Training and evaluation completed successfully!")
    return metrics


if __name__ == "__main__":
    train_and_evaluate()
