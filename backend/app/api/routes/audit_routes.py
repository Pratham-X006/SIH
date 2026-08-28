from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import require_role
from app.db.models import AuditLog, BlockchainTransaction, User
from app.db.session import get_db

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("")
def list_audit_log(
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("DISTRICT_OFFICER", "AUDITOR", "SUPER_ADMIN")),
):
    rows = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(min(limit, 500)).all()
    return [
        {
            "id": r.id, "actor": r.actor, "action": r.action, "entity_type": r.entity_type,
            "entity_id": r.entity_id, "details": r.details_json, "timestamp": r.timestamp.isoformat(),
        }
        for r in rows
    ]


@router.get("/blockchain/transactions")
def list_blockchain_transactions(limit: int = 100, db: Session = Depends(get_db)):
    """Public-safe: transaction metadata only, no PII (Section 39/40)."""
    rows = db.query(BlockchainTransaction).order_by(BlockchainTransaction.timestamp.desc()).limit(min(limit, 500)).all()
    return [
        {
            "id": r.id, "related_entity_type": r.related_entity_type, "related_entity_id": r.related_entity_id,
            "event_type": r.event_type, "tx_hash": r.tx_hash, "timestamp": r.timestamp.isoformat(),
        }
        for r in rows
    ]
