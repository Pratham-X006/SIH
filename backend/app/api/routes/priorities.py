from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import PriorityScore, Zone
from app.db.session import get_db
from app.models.schemas import ComputePrioritiesRequest
from app.services.priority_engine import ZoneInput, compute_priorities

router = APIRouter(prefix="/api/priorities", tags=["priorities"])


@router.post("/compute")
def compute(payload: ComputePrioritiesRequest, db: Session = Depends(get_db)):
    zone_inputs = []
    zone_lookup: dict[str, Zone] = {}
    for z in payload.zones:
        zone = db.query(Zone).filter(Zone.name == z.zone_name).first()
        if zone is None:
            continue
        zone_lookup[z.zone_name] = zone
        zone_inputs.append(
            ZoneInput(
                zone_id=zone.id,
                zone_name=z.zone_name,
                risk_level=z.risk_level,
                population_exposed=z.population_exposed,
                gross_requirement=z.gross_requirement,
                net_requirement=z.net_requirement,
                urgency=z.urgency,
                accessibility_score=z.accessibility_score,
            )
        )

    results = compute_priorities(zone_inputs)

    for r in results:
        db.add(
            PriorityScore(
                zone_id=r.zone_id,
                disaster_label=payload.disaster_label,
                severity_score=r.severity_score,
                population_norm=r.population_norm,
                resource_deficit_norm=r.resource_deficit_norm,
                urgency=r.urgency,
                accessibility_score=r.accessibility_score,
                priority_score=r.priority_score,
                explanation_json=r.explanation,
            )
        )
    db.commit()

    return [
        {
            "zone_id": r.zone_id,
            "zone_name": r.zone_name,
            "priority_score": r.priority_score,
            "rank": r.explanation["rank"],
            "severity_score": r.severity_score,
            "population_norm": r.population_norm,
            "resource_deficit_norm": r.resource_deficit_norm,
            "urgency": r.urgency,
            "accessibility_score": r.accessibility_score,
            "explanation": r.explanation,
        }
        for r in results
    ]


@router.get("")
def list_priorities(disaster_label: str | None = None, db: Session = Depends(get_db)):
    q = db.query(PriorityScore)
    if disaster_label:
        q = q.filter(PriorityScore.disaster_label == disaster_label)
    rows = q.order_by(PriorityScore.priority_score.desc()).all()
    return [
        {
            "id": r.id,
            "zone_id": r.zone_id,
            "disaster_label": r.disaster_label,
            "priority_score": r.priority_score,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
