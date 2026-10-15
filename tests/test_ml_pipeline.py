"""Tests for Phase 2 model artifacts and inference validation."""

from __future__ import annotations

import math
import unittest

from backend.app.ml.predictor import load_metadata, load_model, predict_crop, predict_top_three
from backend.scripts.train_model import (
    DATA_PATH,
    FEATURE_NAMES,
    METADATA_PATH,
    MODEL_PATH,
    validate_dataset,
)


VALID_FEATURES = {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.879744,
    "humidity": 82.002744,
    "ph": 6.502985,
    "rainfall": 202.935536,
}


class TestMLPipeline(unittest.TestCase):
    def test_dataset_schema_validation(self):
        import pandas as pd

        df = pd.read_csv(DATA_PATH)
        validate_dataset(df)
        self.assertEqual(list(df.columns), FEATURE_NAMES + ["label"])

    def test_artifacts_exist_and_metadata_is_complete(self):
        self.assertTrue(MODEL_PATH.exists())
        self.assertTrue(METADATA_PATH.exists())
        metadata = load_metadata()
        self.assertEqual(metadata["feature_names"], FEATURE_NAMES)
        self.assertEqual(metadata["dataset_row_count"], 2200)
        self.assertEqual(metadata["dataset_class_count"], 22)
        self.assertEqual(metadata["train_sample_count"], 1760)
        self.assertEqual(metadata["test_sample_count"], 440)
        self.assertTrue(metadata["model_comparison"])

    def test_model_loading_and_prediction_output(self):
        model = load_model()
        result = predict_crop(VALID_FEATURES, model=model)
        self.assertEqual(
            set(result), {"crop", "candidates", "score_type", "score_explanation"}
        )
        self.assertIsInstance(result["crop"], str)
        self.assertEqual(len(result["candidates"]), 3)
        self.assertEqual(result["score_type"], "probability")
        self.assertEqual(result["candidates"][0]["crop"], result["crop"])
        self.assertTrue(all(0.0 <= item["score"] <= 1.0 for item in result["candidates"]))

    def test_top_three_candidate_predictions(self):
        candidates = predict_top_three(VALID_FEATURES)
        self.assertEqual(len(candidates), 3)
        self.assertEqual(len({candidate["crop"] for candidate in candidates}), 3)
        self.assertGreaterEqual(candidates[0]["score"], candidates[1]["score"])
        self.assertGreaterEqual(candidates[1]["score"], candidates[2]["score"])

    def test_invalid_feature_counts_and_non_finite_inputs(self):
        invalid_inputs = [
            {**VALID_FEATURES, "unexpected": 1},
            {key: value for key, value in VALID_FEATURES.items() if key != "N"},
            {**VALID_FEATURES, "N": math.nan},
            {**VALID_FEATURES, "N": math.inf},
            {**VALID_FEATURES, "N": "not-a-number"},
        ]
        for features in invalid_inputs:
            with self.subTest(features=features):
                with self.assertRaises((TypeError, ValueError)):
                    predict_crop(features)
