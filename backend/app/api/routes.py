"""FastAPI route definitions."""

from __future__ import annotations

import io

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse

from backend.app.schemas.prediction import HistoryResponse, PredictionRequest, PredictionResponse
from backend.app.services.prediction_service import ModelUnavailableError


router = APIRouter(prefix="/api")


def _services(request: Request):
    return request.app.state.prediction_service, request.app.state.analytics_service, request.app.state.history_service


@router.get("/health")
def health(request: Request):
    prediction_service, _, _ = _services(request)
    return {
        "status": "ok" if prediction_service.available else "degraded",
        "model_available": prediction_service.available,
        "service": "krishisathi-ai-backend",
    }


@router.get("/metadata")
def metadata(request: Request):
    _, analytics, _ = _services(request)
    try:
        data = analytics.metadata
    except (FileNotFoundError, OSError):
        raise HTTPException(status_code=503, detail="Model metadata is unavailable")
    return {
        "model_name": data["model_name"],
        "model_version": data["model_version"],
        "feature_names": data["feature_names"],
        "target_name": data["target_name"],
        "target_classes": data["target_classes"],
    }


@router.get("/dashboard/summary")
def dashboard_summary(request: Request):
    try:
        return _services(request)[1].summary()
    except (FileNotFoundError, OSError, KeyError) as exc:
        raise HTTPException(status_code=503, detail="Dashboard data is unavailable") from exc


@router.get("/dashboard/crop-distribution")
def crop_distribution(request: Request):
    try:
        return _services(request)[1].crop_distribution()
    except (FileNotFoundError, OSError, KeyError) as exc:
        raise HTTPException(status_code=503, detail="Dashboard data is unavailable") from exc


@router.get("/dashboard/feature-statistics")
def feature_statistics(request: Request):
    try:
        return _services(request)[1].feature_statistics()
    except (FileNotFoundError, OSError, KeyError) as exc:
        raise HTTPException(status_code=503, detail="Dashboard data is unavailable") from exc


@router.get("/dashboard/model-metrics")
def model_metrics(request: Request):
    try:
        return _services(request)[1].model_metrics()
    except (FileNotFoundError, OSError, KeyError) as exc:
        raise HTTPException(status_code=503, detail="Model metrics are unavailable") from exc


@router.get("/dashboard/confusion-matrix")
def confusion_matrix(request: Request):
    try:
        return _services(request)[1].confusion_matrix()
    except (FileNotFoundError, OSError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Confusion matrix is unavailable") from exc


@router.get("/dashboard/feature-importance")
def feature_importance(request: Request):
    try:
        return _services(request)[1].feature_importance()
    except (FileNotFoundError, OSError, KeyError) as exc:
        raise HTTPException(status_code=503, detail="Feature importance is unavailable") from exc


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def predict(payload: PredictionRequest, request: Request):
    prediction_service, _, _ = _services(request)
    try:
        return prediction_service.predict(payload)
    except ModelUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Crop recommendation model is unavailable") from exc
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=500, detail="Prediction could not be completed") from exc


@router.get("/history", response_model=HistoryResponse)
def history(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    items = _services(request)[2].list(limit=limit, offset=offset)
    return {"items": items, "limit": limit, "offset": offset, "count": len(items)}


@router.get("/history/export")
def history_export(request: Request):
    content = _services(request)[2].export_csv()
    return StreamingResponse(
        io.StringIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=krishisathi-history.csv"},
    )


@router.get("/history/{prediction_id}")
def history_detail(prediction_id: int, request: Request):
    item = _services(request)[2].get(prediction_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Prediction history record not found")
    return item


@router.delete("/history/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
def history_delete(prediction_id: int, request: Request):
    if not _services(request)[2].delete(prediction_id):
        raise HTTPException(status_code=404, detail="Prediction history record not found")
