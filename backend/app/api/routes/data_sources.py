from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import DataSource
from app.db.session import get_db

router = APIRouter(prefix="/api/data-sources", tags=["data-sources"])


@router.get("")
def list_data_sources(db: Session = Depends(get_db)):
    """Machine-readable version of docs/DATA_SOURCES.md — powers REAL/DERIVED/SYNTHETIC/
    SIMULATED provenance badges in the UI (Section 72)."""
    rows = db.query(DataSource).all()
    return [
        {
            "name": r.name, "category": r.category, "source": r.source, "url": r.url,
            "temporal_coverage": r.temporal_coverage, "spatial_coverage": r.spatial_coverage,
            "resolution": r.resolution, "variables": r.variables, "processing": r.processing,
            "license": r.license, "limitations": r.limitations,
        }
        for r in rows
    ]
