"""Automated test suite for Emotion Classifier model predictions."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.emotion_classifier import predict_emotion


class TestEmotionClassifier(unittest.TestCase):

    def test_benchmark_sentences(self):
        test_cases = [
            ("I am happy", ["Happy", "Excited"]),
            ("I am not happy", ["Sad"]),
            ("I'm stressed", ["Stress"]),
            ("I am excited", ["Excited"]),
            ("I couldn't sleep", ["Stress", "Anxiety"]),
            ("I feel lonely", ["Sad"]),
            ("I'm worried about tomorrow's exam", ["Anxiety"]),
            ("I had a wonderful day", ["Happy", "Excited"]),
        ]

        print("\n" + "=" * 60)
        print("RUNNING AUTOMATED EMOTION CLASSIFIER TESTS")
        print("=" * 60)

        for text, expected_emotions in test_cases:
            res = predict_emotion(text)
            pred_emo = res["emotion"]
            confidence = res["confidence"]

            print(f"Test Sentence: \"{text}\"")
            print(f"  -> Predicted Emotion: {pred_emo}")
            print(f"  -> Confidence:        {confidence:.2%}")
            print(f"  -> Expected:          {expected_emotions}")

            self.assertIn(
                pred_emo,
                expected_emotions,
                f"Failed for sentence '{text}': expected one of {expected_emotions}, got '{pred_emo}'"
            )
            print("  [OK] PASSED\n" + "-" * 40)



if __name__ == "__main__":
    unittest.main()
