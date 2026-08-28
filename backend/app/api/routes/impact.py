from fastapi import APIRouter, HTTPException

from app.models.schemas import ImpactRequest, ReliefRequest
from app.services import gis_impact, relief_estimator

router = APIRouter(tags=["impact"])


@router.get("/impact/districts")
def districts():
    return gis_impact.list_districts()


@router.post("/impact/assessment")
def impact_assessment(payload: ImpactRequest):
    try:
        return gis_impact.assess_impact(payload.district, payload.risk_score)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/relief/estimate")
def relief_estimate(payload: ReliefRequest):
    estimate = relief_estimator.estimate_relief(payload.exposed_population, payload.relief_days)
    return estimate.__dict__
