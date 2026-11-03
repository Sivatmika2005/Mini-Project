# Emotion Classification Model Training Pipeline

This directory contains the machine learning training pipeline for the **AI Wellness Chatbot Emotion Classifier**.

The classifier categorizes text into 10 target emotion categories:
- `Happy`, `Sad`, `Anxious`, `Stressed`, `Angry`, `Fear`, `Neutral`, `Excited`, `Lonely`, `Overwhelmed`

---

## 📁 Directory Structure

```
training/
├── config.py                  # Training configuration, hyperparameters & label mappings
├── prepare_dataset.py         # Parses, cleans & normalizes raw emotion datasets
├── train_emotion_model.py     # Train/Val/Test split, model training & metric evaluation
├── evaluate_model.py          # Standalone evaluation & confusion matrix generator
├── predict.py                 # CLI tool for emotion prediction on arbitrary text
├── requirements_training.txt  # Training & ML dependencies
├── data/                      # Processed datasets directory
└── README.md                  # Comprehensive training guide
```

---

## 🚀 Step 1: Install Training Dependencies

Ensure all required ML dependencies are installed:

```bash
pip install -r training/requirements_training.txt
```

---

## 📊 Step 2: Prepare Datasets

The pipeline supports three major benchmark datasets:
1. **GoEmotions**: Place `goemotions.csv` inside `datasets/goemotions.csv` (already supported).
2. **DAIR Emotion Dataset**: Place `dair_emotion.csv` inside `datasets/dair_emotion.csv` (optional).
3. **Empathetic Dialogues**: Place `empathetic_dialogues.csv` inside `datasets/empathetic_dialogues.csv` (optional).

Run the dataset preparation script:

```bash
python training/prepare_dataset.py
```

This automatically cleans text, maps fine-grained labels onto the 10 target classes, balances class distribution, and exports `training/data/processed_emotions.csv`.

---

## 🏋️ Step 3: Train the Emotion Classifier

Run the training pipeline:

```bash
python training/train_emotion_model.py
```

### What this script does:
1. Splits dataset into **Train (70%)**, **Validation (15%)**, and **Test (15%)** sets.
2. Extracts sublinear TF-IDF unigram and bigram features (15,000 max features).
3. Trains a regularized classifier with loss tracking across epochs.
4. Calibrates probabilities using `CalibratedClassifierCV` for reliable confidence scoring.
5. Computes Accuracy, Weighted/Macro Precision, Recall, and F1-Score metrics.
6. Generates and saves:
   - Confusion Matrix heatmap: `models/confusion_matrix.png`
   - Training/Validation Loss curve: `models/training_loss.png`
   - Trained model artifacts: `models/emotion_classifier.joblib`
   - Performance metrics JSON: `models/metadata.json`

---

## 📈 Step 4: Evaluate the Trained Model

To run an independent evaluation of the saved model:

```bash
python training/evaluate_model.py
```

This outputs detailed per-class classification metrics (Precision, Recall, F1) and saves `training/eval_confusion_matrix.png`.

---

## 🔮 Step 5: Test Prediction via CLI

Test any custom message directly from the command line:

```bash
python training/predict.py "I am feeling so anxious and scared about my exam tomorrow"
```

Example Output:
```
==================================================
EMOTION PREDICTION RESULT
==================================================
Input Text:        "I am feeling so anxious and scared about my exam tomorrow"
Predicted Emotion: Anxious
Confidence Score:  92.45%
--------------------------------------------------
Top Probabilities:
  - Anxious     : 92.45%
  - Fear        : 4.12%
  - Stressed    : 2.10%
  - Sad         : 0.83%
  - Neutral     : 0.50%
==================================================
```

---

## 🤖 Step 6: How the Chatbot Uses the Trained Model

1. **Inference Pipeline (`utils/llm.py`)**:
   - User message is classified by `utils/emotion_classifier.py` returning `(predicted_emotion, confidence_score)`.
   - The user's recent check-in mood, stress level (0–10), and latest journal summary are retrieved from the database.
   - All 4 signals are formatted into the LLM system context so responses are deeply personalized.

2. **Emotion-Aware Fallback**:
   - If the external LLM API is offline or unconfigured, the chatbot uses the trained emotion classifier to generate empathetic, supportive fallback responses tailored to the user's emotion and stress level, replacing static keyword matching.
