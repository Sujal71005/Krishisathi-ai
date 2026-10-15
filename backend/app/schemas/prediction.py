"""Request and response models for crop recommendations."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    N: float = Field(..., ge=0, le=1000, description="Soil nitrogen value")
    P: float = Field(..., ge=0, le=1000, description="Soil phosphorus value")
    K: float = Field(..., ge=0, le=1000, description="Soil potassium value")
    temperature: float = Field(..., ge=-50, le=70, description="Temperature in degrees Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity percentage")
    ph: float = Field(..., ge=0, le=14, description="Soil pH")
    rainfall: float = Field(..., ge=0, le=10000, description="Rainfall measurement")

    @field_validator("N", "P", "K", "temperature", "humidity", "ph", "rainfall", mode="before")
    @classmethod
    def finite_number(cls, value: float) -> float:
        if isinstance(value, (bool, str)):
            raise ValueError("Feature values must be numeric")
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Feature values must be numeric") from exc
        if not math.isfinite(numeric):
            raise ValueError("All feature values must be finite")
        return numeric


class PredictionResponse(BaseModel):
    prediction_id: int
    timestamp: datetime
    model_name: str
    model_version: str
    input_features: dict[str, float]
    crop: str
    candidates: list[dict[str, Any]]
    score_type: str
    score_explanation: str
    warnings: list[str]


class HistoryItem(BaseModel):
    prediction_id: int
    timestamp: datetime
    model_name: str
    model_version: str
    input_features: dict[str, float]
    result: dict[str, Any]


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    limit: int
    offset: int
    count: int
