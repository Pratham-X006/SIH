"""One helper so every state-changing route logs consistently (Section 53)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import AuditLog


def log_action(
    db: Session, actor: str, action: str, entity_type: str | None = None,
    entity_id: int | None = None, details: dict | None = None
) -> None:
    db.add(
        AuditLog(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details_json=details or {},
        )
    )
    db.commit()
