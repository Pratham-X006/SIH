from fastapi import APIRouter

from app.models.schemas import RiskPredictRequest
from app.services.risk_model import risk_model

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/flood-risk")
def predict_flood_risk(payload: RiskPredictRequest):
    return risk_model.predict(**payload.model_dump())


@router.get("/model-status")
def model_status():
    return {"is_trained": risk_model.is_trained}
