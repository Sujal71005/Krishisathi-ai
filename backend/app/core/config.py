"""Path and runtime configuration for the local FastAPI service."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    dataset_path: Path = PROJECT_ROOT / "data" / "Crop_recommendation.csv"
    model_path: Path = PROJECT_ROOT / "backend" / "models" / "crop_model.joblib"
    metadata_path: Path = PROJECT_ROOT / "backend" / "models" / "model_metadata.json"
    database_path: Path = PROJECT_ROOT / "backend" / "data" / "krishisathi.db"
    allowed_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")

    @classmethod
    def from_environment(cls) -> "Settings":
        origins = tuple(
            origin.strip()
            for origin in os.getenv(
                "KRISHISATHI_ALLOWED_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if origin.strip()
        )
        return cls(
            dataset_path=Path(os.getenv("KRISHISATHI_DATASET_PATH", str(cls.dataset_path))),
            model_path=Path(os.getenv("KRISHISATHI_MODEL_PATH", str(cls.model_path))),
            metadata_path=Path(os.getenv("KRISHISATHI_METADATA_PATH", str(cls.metadata_path))),
            database_path=Path(os.getenv("KRISHISATHI_DATABASE_PATH", str(cls.database_path))),
            allowed_origins=origins,
        )
