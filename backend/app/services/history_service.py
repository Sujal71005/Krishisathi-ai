"""SQLite-backed prediction history service."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.app.database.connection import connect, initialize_database
from backend.app.database.models import row_to_prediction


class HistoryService:
    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(self.database_path)

    def insert(
        self,
        input_features: dict[str, float],
        result: dict[str, Any],
        model_name: str,
        model_version: str,
    ) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        with connect(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO predictions
                    (created_at, model_name, model_version, input_features, result)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    model_name,
                    model_version,
                    json.dumps(input_features, sort_keys=True),
                    json.dumps(result, sort_keys=True),
                ),
            )
            prediction_id = cursor.lastrowid
        return self.get(int(prediction_id))

    def list(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        with connect(self.database_path) as connection:
            rows = connection.execute(
                "SELECT * FROM predictions ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [row_to_prediction(row) for row in rows]

    def get(self, prediction_id: int) -> dict[str, Any] | None:
        with connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT * FROM predictions WHERE id = ?", (prediction_id,)
            ).fetchone()
        return row_to_prediction(row) if row else None

    def delete(self, prediction_id: int) -> bool:
        with connect(self.database_path) as connection:
            cursor = connection.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
        return cursor.rowcount == 1

    def export_csv(self) -> str:
        rows = self.list(limit=100000, offset=0)
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "prediction_id",
                "timestamp",
                "model_name",
                "model_version",
                "input_features",
                "crop",
                "score_type",
            ],
        )
        writer.writeheader()
        for item in rows:
            result = item["result"]
            writer.writerow(
                {
                    "prediction_id": item["prediction_id"],
                    "timestamp": item["timestamp"],
                    "model_name": item["model_name"],
                    "model_version": item["model_version"],
                    "input_features": json.dumps(item["input_features"], sort_keys=True),
                    "crop": result.get("crop", ""),
                    "score_type": result.get("score_type", ""),
                }
            )
        return output.getvalue()
