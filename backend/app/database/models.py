"""Database record conversion helpers."""

from __future__ import annotations

import json
from typing import Any


def row_to_prediction(row: Any) -> dict[str, Any]:
    return {
        "prediction_id": int(row["id"]),
        "timestamp": row["created_at"],
        "model_name": row["model_name"],
        "model_version": row["model_version"],
        "input_features": json.loads(row["input_features"]),
        "result": json.loads(row["result"]),
    }
