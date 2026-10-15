"""Cached analytics sourced from the real dataset and model metadata."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.ml.predictor import load_metadata, load_model


class AnalyticsService:
    def __init__(self, dataset_path: str | Path, model_path: str | Path, metadata_path: str | Path):
        self.dataset_path = Path(dataset_path)
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)

    @property
    @lru_cache(maxsize=1)
    def frame(self) -> pd.DataFrame:
        if not self.dataset_path.exists():
            raise FileNotFoundError("Dataset is unavailable")
        return pd.read_csv(self.dataset_path)

    @property
    @lru_cache(maxsize=1)
    def metadata(self) -> dict[str, Any]:
        return load_metadata(self.metadata_path)

    @property
    @lru_cache(maxsize=1)
    def model(self) -> Any:
        return load_model(self.model_path)

    def summary(self) -> dict[str, Any]:
        metadata = self.metadata
        return {
            "dataset_rows": int(len(self.frame)),
            "feature_count": len(metadata["feature_names"]),
            "crop_class_count": int(self.frame[metadata["target_name"]].nunique()),
            "target_name": metadata["target_name"],
            "model_name": metadata["model_name"],
            "model_version": metadata["model_version"],
            "training_timestamp": metadata["training_timestamp"],
        }

    def crop_distribution(self) -> dict[str, Any]:
        target = self.metadata["target_name"]
        counts = self.frame[target].value_counts().sort_index()
        return {
            "items": [{"crop": str(name), "count": int(count)} for name, count in counts.items()],
            "total": int(counts.sum()),
        }

    def feature_statistics(self) -> dict[str, Any]:
        features = self.metadata["feature_names"]
        stats = self.frame[features].describe().T
        items = []
        for name, row in stats.iterrows():
            items.append(
                {
                    "feature": name,
                    "count": int(row["count"]),
                    "mean": float(row["mean"]),
                    "std": float(row["std"]),
                    "min": float(row["min"]),
                    "q25": float(row["25%"]),
                    "median": float(row["50%"]),
                    "q75": float(row["75%"]),
                    "max": float(row["max"]),
                }
            )
        return {"items": items}

    def model_metrics(self) -> dict[str, Any]:
        metadata = self.metadata
        return {
            "model_name": metadata["model_name"],
            "model_version": metadata["model_version"],
            "selection_criterion": metadata["model_selection_criterion"],
            "cross_validation": metadata["cross_validation"],
            "comparison": metadata["model_comparison"],
            "selected_model_cv": metadata["selected_model_cv"],
            "held_out_test": metadata["evaluation_metrics"],
        }

    def confusion_matrix(self) -> dict[str, Any]:
        metadata = self.metadata
        labels = metadata["target_classes"]
        matrix = metadata["evaluation_metrics"]["confusion_matrix"]
        if len(matrix) != len(labels) or any(len(row) != len(labels) for row in matrix):
            raise ValueError("Saved confusion matrix does not match saved class ordering")
        return {"labels": labels, "matrix": matrix, "row_axis": "actual", "column_axis": "predicted"}

    def feature_importance(self) -> dict[str, Any]:
        model = self.model
        if hasattr(model, "feature_importances_"):
            values = model.feature_importances_
        elif hasattr(model, "named_steps"):
            estimator = list(model.named_steps.values())[-1]
            if not hasattr(estimator, "feature_importances_"):
                return {"supported": False, "items": []}
            values = estimator.feature_importances_
        else:
            return {"supported": False, "items": []}
        return {
            "supported": True,
            "items": [
                {"feature": name, "importance": float(value)}
                for name, value in zip(self.metadata["feature_names"], values)
            ],
        }
