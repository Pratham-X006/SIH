"""GET /api/system/status — component-level health (Section 56). Every failure mode from
LIMITATIONS.md's failure matrix should be visible here, not discovered by a judge clicking
around a broken dashboard."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.blockchain_service import blockchain_client
from app.services.risk_model import risk_model

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/status")
def system_status(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:  # noqa: BLE001
        db_status = f"error: {exc}"

    ml_status = "trained_model_loaded" if risk_model.is_trained else "fallback_heuristic_active (no trained model.joblib found)"
    blockchain_status = "ready" if blockchain_client.is_ready else "not_deployed (run blockchain/scripts/deploy.js)"

    overall = "ok" if db_status == "ok" else "degraded"

    return {
        "database": db_status,
        "ml_model": ml_status,
        "blockchain": blockchain_status,
        "live_data_sources": "not polled by this endpoint — see GET /hazards/live for a live check",
        "overall": overall,
    }
