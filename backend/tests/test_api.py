"""Backend route and service contract tests with an isolated SQLite database.

The execution sandbox blocks local sockets and its Python 3.14/httpx client
combination hangs, so these tests call the real route functions directly while
still using the real model, CSV, Pydantic schemas, and SQLite store.
"""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import HTTPException
from starlette.middleware.cors import CORSMiddleware

from backend.app.api.routes import (
    confusion_matrix,
    crop_distribution,
    dashboard_summary,
    feature_importance,
    feature_statistics,
    health,
    history,
    history_delete,
    history_detail,
    history_export,
    metadata,
    model_metrics,
    predict,
)
from backend.app.core.config import PROJECT_ROOT, Settings
from backend.app.main import create_app
from backend.app.schemas.prediction import PredictionRequest


VALID_PAYLOAD = {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.879744,
    "humidity": 82.002744,
    "ph": 6.502985,
    "rainfall": 202.935536,
}


def run(coroutine):
    return coroutine


class TestKrishiSathiAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(dir=PROJECT_ROOT)
        root = Path(cls.temp_dir.name)
        settings = Settings(
            dataset_path=PROJECT_ROOT / "data" / "Crop_recommendation.csv",
            model_path=PROJECT_ROOT / "backend" / "models" / "crop_model.joblib",
            metadata_path=PROJECT_ROOT / "backend" / "models" / "model_metadata.json",
            database_path=root / "test-history.sqlite3",
            allowed_origins=("http://localhost:5173",),
        )
        cls.app = create_app(settings)
        cls.request = SimpleNamespace(app=cls.app)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_health_endpoint(self):
        body = run(health(self.request))
        self.assertEqual(body["status"], "ok")
        self.assertTrue(body["model_available"])

    def test_metadata_endpoint(self):
        body = run(metadata(self.request))
        self.assertEqual(body["feature_names"], ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])
        self.assertEqual(len(body["target_classes"]), 22)

    def test_dashboard_analytics_and_class_counts(self):
        self.assertEqual(run(dashboard_summary(self.request))["dataset_rows"], 2200)
        self.assertEqual(run(dashboard_summary(self.request))["crop_class_count"], 22)
        distribution = run(crop_distribution(self.request))
        self.assertEqual(len(distribution["items"]), 22)
        self.assertTrue(all(item["count"] == 100 for item in distribution["items"]))
        self.assertEqual(len(run(feature_statistics(self.request))["items"]), 7)
        self.assertEqual(run(model_metrics(self.request))["held_out_test"]["accuracy"], 0.9931818181818182)
        matrix = run(confusion_matrix(self.request))
        self.assertEqual(len(matrix["labels"]), 22)
        self.assertEqual(len(matrix["matrix"]), 22)
        importance = run(feature_importance(self.request))
        self.assertTrue(importance["supported"])
        self.assertEqual(len(importance["items"]), 7)

    def test_valid_prediction_top_three_and_persistence(self):
        body = run(predict(PredictionRequest(**VALID_PAYLOAD), self.request))
        self.assertEqual(body["crop"], "rice")
        self.assertEqual(len(body["candidates"]), 3)
        self.assertEqual(body["score_type"], "probability")
        self.assertEqual(body["warnings"], [])
        prediction_id = body["prediction_id"]

        detail = run(history_detail(prediction_id, self.request))
        self.assertEqual(detail["prediction_id"], prediction_id)
        listing = run(history(self.request, limit=10, offset=0))
        self.assertTrue(any(item["prediction_id"] == prediction_id for item in listing["items"]))
        export_response = run(history_export(self.request))
        self.assertEqual(export_response.media_type, "text/csv")
        self.assertIn("krishisathi-history.csv", export_response.headers["content-disposition"])
        self.assertIn(str(prediction_id), self.app.state.history_service.export_csv())

    def test_invalid_missing_nonfinite_and_out_of_supported_range_inputs(self):
        missing = dict(VALID_PAYLOAD)
        del missing["ph"]
        with self.assertRaises(Exception):
            PredictionRequest(**missing)

        nonfinite = dict(VALID_PAYLOAD)
        nonfinite["N"] = math.nan
        with self.assertRaises(Exception):
            PredictionRequest(**nonfinite)

        negative = dict(VALID_PAYLOAD)
        negative["rainfall"] = -1
        with self.assertRaises(Exception):
            PredictionRequest(**negative)

        malformed = dict(VALID_PAYLOAD)
        malformed["N"] = "90"
        with self.assertRaises(Exception):
            PredictionRequest(**malformed)

        observed_outside_but_supported = dict(VALID_PAYLOAD)
        observed_outside_but_supported["N"] = 500
        body = run(predict(PredictionRequest(**observed_outside_but_supported), self.request))
        self.assertTrue(body["warnings"])

    def test_delete_and_not_found_behavior(self):
        body = run(predict(PredictionRequest(**VALID_PAYLOAD), self.request))
        prediction_id = body["prediction_id"]
        self.assertIsNone(run(history_delete(prediction_id, self.request)))
        with self.assertRaises(HTTPException) as context:
            run(history_detail(prediction_id, self.request))
        self.assertEqual(context.exception.status_code, 404)
        with self.assertRaises(HTTPException) as context:
            run(history_delete(prediction_id, self.request))
        self.assertEqual(context.exception.status_code, 404)

    def test_cors_configuration(self):
        middleware = next(item for item in self.app.user_middleware if item.cls is CORSMiddleware)
        self.assertEqual(middleware.kwargs["allow_origins"], ["http://localhost:5173"])
        self.assertTrue(middleware.kwargs["allow_credentials"])

    def test_missing_model_is_reported_without_stack_trace(self):
        root = Path(self.temp_dir.name)
        settings = Settings(
            dataset_path=PROJECT_ROOT / "data" / "Crop_recommendation.csv",
            model_path=root / "missing.joblib",
            metadata_path=PROJECT_ROOT / "backend" / "models" / "model_metadata.json",
            database_path=root / "missing-model.sqlite3",
        )
        app = create_app(settings)
        request = SimpleNamespace(app=app)
        self.assertEqual(run(health(request))["status"], "degraded")
        with self.assertRaises(HTTPException) as context:
            run(predict(PredictionRequest(**VALID_PAYLOAD), request))
        self.assertEqual(context.exception.status_code, 503)
        self.assertNotIn("Traceback", str(context.exception.detail))


if __name__ == "__main__":
    unittest.main()
