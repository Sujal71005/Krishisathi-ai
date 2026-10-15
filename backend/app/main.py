"""KrishiSathi AI FastAPI application factory and local entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router
from backend.app.core.config import Settings
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.history_service import HistoryService
from backend.app.services.prediction_service import PredictionService


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()
    app = FastAPI(
        title="KrishiSathi AI API",
        description="Crop suitability recommendations and dashboard analytics.",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    history_service = HistoryService(settings.database_path)
    app.state.history_service = history_service
    app.state.prediction_service = PredictionService(
        model_path=settings.model_path,
        metadata_path=settings.metadata_path,
        dataset_path=settings.dataset_path,
        history_service=history_service,
    )
    app.state.analytics_service = AnalyticsService(
        dataset_path=settings.dataset_path,
        model_path=settings.model_path,
        metadata_path=settings.metadata_path,
    )
    app.include_router(router)
    return app


app = create_app()
