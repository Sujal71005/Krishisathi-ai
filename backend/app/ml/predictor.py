"""Inference helpers for the persisted crop recommendation pipeline."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "backend" / "models" / "crop_model.joblib"
DEFAULT_METADATA_PATH = PROJECT_ROOT / "backend" / "models" / "model_metadata.json"


def load_model(model_path: str | Path = DEFAULT_MODEL_PATH) -> Any:
    """Load the fitted pipeline from disk; this does not retrain it."""
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model artifact not found at {path}")
    return joblib.load(path)


def load_metadata(metadata_path: str | Path = DEFAULT_METADATA_PATH) -> dict[str, Any]:
    path = Path(metadata_path)
    if not path.exists():
        raise FileNotFoundError(f"Metadata artifact not found at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_features(
    features: Mapping[str, Any], feature_names: list[str] | None = None
) -> list[float]:
    """Validate names, order, numeric values, and finiteness of one input."""
    names = feature_names or load_metadata()["feature_names"]
    if not isinstance(features, Mapping):
        raise TypeError("features must be a mapping of feature names to values")
    if set(features) != set(names):
        missing = [name for name in names if name not in features]
        extra = [name for name in features if name not in names]
        raise ValueError(f"Invalid feature names; missing={missing}, extra={extra}")
    values: list[float] = []
    for name in names:
        value = features[name]
        if isinstance(value, bool):
            raise ValueError(f"Feature {name} must be numeric, not boolean")
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Feature {name} must be numeric") from exc
        if not math.isfinite(numeric):
            raise ValueError(f"Feature {name} must be finite")
        values.append(numeric)
    return values


def _score_details(model: Any, row: np.ndarray, classes: list[str]) -> tuple[str, np.ndarray]:
    if hasattr(model, "predict_proba"):
        probabilities = np.asarray(model.predict_proba(row)[0], dtype=float)
        return "probability", probabilities
    if hasattr(model, "decision_function"):
        decision = np.asarray(model.decision_function(row), dtype=float)
        if decision.ndim == 2:
            decision = decision[0]
        return "uncalibrated_decision_score", decision
    return "unavailable", np.full(len(classes), np.nan)


def predict_crop(
    features: Mapping[str, Any],
    model: Any | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the top crop and up to three scored candidates.

    For the persisted classifiers in this project, scores are probabilities
    from ``predict_proba``. The response labels the score type explicitly;
    probabilities are not presented as calibrated real-world risk.
    """
    metadata = metadata or load_metadata()
    values = validate_features(features, metadata["feature_names"])
    model = model or load_model()
    row = pd.DataFrame([values], columns=metadata["feature_names"], dtype=float)
    prediction = str(model.predict(row)[0])
    classes = [str(value) for value in getattr(model, "classes_", metadata["target_classes"])]
    score_type, scores = _score_details(model, row, classes)
    order = np.argsort(np.nan_to_num(scores, nan=-np.inf))[::-1][:3]
    candidates = [
        {"crop": classes[index], "score": None if not np.isfinite(scores[index]) else float(scores[index])}
        for index in order
    ]
    return {
        "crop": prediction,
        "candidates": candidates,
        "score_type": score_type,
        "score_explanation": (
            "Scores are model probabilities from predict_proba; they are not calibrated agronomic risk estimates."
            if score_type == "probability"
            else "Scores are uncalibrated model decision scores, not probabilities."
            if score_type == "uncalibrated_decision_score"
            else "This model does not expose prediction scores."
        ),
    }


def predict_top_three(features: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Convenience wrapper returning only the candidate list."""
    return predict_crop(features)["candidates"]
