"""Prediction orchestration, validation warnings, and persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.ml.predictor import load_metadata, load_model, predict_crop
from backend.app.schemas.prediction import PredictionRequest
from backend.app.services.history_service import HistoryService


class ModelUnavailableError(RuntimeError):
    """Raised when the persisted model or metadata cannot be loaded."""


class PredictionService:
    def __init__(
        self,
        model_path: str | Path,
        metadata_path: str | Path,
        dataset_path: str | Path,
        history_service: HistoryService,
    ):
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.dataset_path = Path(dataset_path)
        self.history_service = history_service
        self.model: Any | None = None
        self.metadata: dict[str, Any] | None = None
        self.load_error: str | None = None
        self.dataset_error: str | None = None
        try:
            self.metadata = load_metadata(self.metadata_path)
            self.model = load_model(self.model_path)
        except (FileNotFoundError, OSError, ValueError, ImportError) as exc:
            self.load_error = str(exc)

        self.observed_ranges: dict[str, tuple[float, float]] = {}
        try:
            if not self.dataset_path.exists():
                raise FileNotFoundError("Dataset is unavailable")
            frame = pd.read_csv(self.dataset_path)
            feature_names = (self.metadata or {}).get("feature_names", [])
            if not feature_names or not all(name in frame.columns for name in feature_names):
                raise ValueError("Dataset does not contain the model feature schema")
            self.observed_ranges = {
                name: (float(frame[name].min()), float(frame[name].max()))
                for name in feature_names
            }
        except (FileNotFoundError, OSError, ValueError, pd.errors.ParserError) as exc:
            self.dataset_error = str(exc)

    @property
    def available(self) -> bool:
        return (
            self.model is not None
            and self.metadata is not None
            and self.dataset_error is None
            and bool(self.observed_ranges)
        )

    def predict(self, request: PredictionRequest) -> dict[str, Any]:
        if not self.available:
            raise ModelUnavailableError("The crop recommendation model is unavailable")
        assert self.metadata is not None
        input_features = request.model_dump()
        warnings = [
            f"{name}={value} is outside the observed dataset range [{low}, {high}]."
            for name, value in input_features.items()
            if name in self.observed_ranges
            for low, high in [self.observed_ranges[name]]
            if value < low or value > high
        ]
        result = predict_crop(input_features, model=self.model, metadata=self.metadata)
        persisted = self.history_service.insert(
            input_features=input_features,
            result={**result, "warnings": warnings},
            model_name=self.metadata["model_name"],
            model_version=self.metadata["model_version"],
        )
        return {
            "prediction_id": persisted["prediction_id"],
            "timestamp": persisted["timestamp"],
            "model_name": self.metadata["model_name"],
            "model_version": self.metadata["model_version"],
            "input_features": input_features,
            **result,
            "warnings": warnings,
        }
