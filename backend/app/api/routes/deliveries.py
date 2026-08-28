"""Dispatch -> receipt -> verification, with automatic discrepancy detection (Section 29).

Quantity comparison happens HERE, off-chain, before anything is asserted to the ledger —
per the masterplan's explicit warning that blockchain does not itself validate truth
(Section 28): the backend compares dispatched vs. received and only then tells the chain
which assertion to record (confirmDelivery vs. flagDiscrepancy). Neither quantity is ever
silently overwritten.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import require_role
from app.db.models import Allocation, BlockchainTransaction, Discrepancy, User
from app.db.session import get_db
from app.models.schemas import ConfirmDeliveryRequest, RecordDispatchRequest, ResolveDiscrepancyRequest
from app.services.audit import log_action
from app.services.blockchain_service import BlockchainNotDeployedError, blockchain_client

router = APIRouter(prefix="/api/deliveries", tags=["deliveries"])


@router.post("/dispatch")
def dispatch(
    payload: RecordDispatchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("WAREHOUSE_MANAGER", "SUPER_ADMIN")),
):
    allocation = db.query(Allocation).filter(Allocation.id == payload.allocation_id).first()
    if allocation is None:
        raise HTTPException(status_code=404, detail="Unknown allocation_id")
    if allocation.status != "ALLOCATED":
        raise HTTPException(status_code=409, detail=f"Allocation must be ALLOCATED first (currently {allocation.status})")

    allocation.quantity_dispatched = payload.quantity_dispatched
    allocation.status = "DISPATCHED"
    allocation.dispatched_at = datetime.now(timezone.utc)

    blockchain_note = "not attempted"
    if allocation.chain_allocation_id is not None:
        try:
            chain_result = blockchain_client.mark_dispatched(allocation.chain_allocation_id)
            db.add(BlockchainTransaction(related_entity_id=allocation.id, event_type="dispatch", tx_hash=chain_result["tx_hash"]))
            blockchain_note = "recorded on-chain"
        except BlockchainNotDeployedError as exc:
            blockchain_note = f"blockchain unavailable: {exc}"
    db.commit()

    log_action(db, actor=user.username, action="dispatch", entity_type="allocation", entity_id=allocation.id, details={"quantity_dispatched": payload.quantity_dispatched, "blockchain_note": blockchain_note})
    return {"allocation_id": allocation.id, "status": allocation.status, "blockchain_note": blockchain_note}


@router.post("/confirm")
def confirm_delivery(
    payload: ConfirmDeliveryRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("RELIEF_CENTRE", "NGO", "SUPER_ADMIN")),
):
    allocation = db.query(Allocation).filter(Allocation.id == payload.allocation_id).first()
    if allocation is None:
        raise HTTPException(status_code=404, detail="Unknown allocation_id")
    if allocation.status != "DISPATCHED":
        raise HTTPException(status_code=409, detail=f"Allocation must be DISPATCHED first (currently {allocation.status})")

    allocation.quantity_received = payload.quantity_received
    allocation.delivered_at = datetime.now(timezone.utc)
    difference = round((allocation.quantity_dispatched or 0) - payload.quantity_received, 4)

    blockchain_note = "not attempted"
    if abs(difference) < 1e-6:
        allocation.status = "VERIFIED"
        if allocation.chain_allocation_id is not None:
            try:
                chain_result = blockchain_client.confirm_delivery(allocation.chain_allocation_id)
                db.add(BlockchainTransaction(related_entity_id=allocation.id, event_type="confirm_delivery", tx_hash=chain_result["tx_hash"]))
                blockchain_note = "recorded on-chain: VERIFIED"
            except BlockchainNotDeployedError as exc:
                blockchain_note = f"blockchain unavailable: {exc}"
        db.commit()
        log_action(db, actor=user.username, action="delivery_verified", entity_type="allocation", entity_id=allocation.id)
        return {"allocation_id": allocation.id, "status": "VERIFIED", "blockchain_note": blockchain_note}

    # Mismatch — create a discrepancy, never silently accept the received figure as correct.
    allocation.status = "DISCREPANCY"
    discrepancy = Discrepancy(
        allocation_id=allocation.id,
        expected_quantity=allocation.quantity_dispatched or 0,
        received_quantity=payload.quantity_received,
        difference=difference,
        reported_by=user.username,
        status="OPEN",
    )
    db.add(discrepancy)
    db.flush()

    if allocation.chain_allocation_id is not None:
        try:
            reason = f"dispatched={allocation.quantity_dispatched} received={payload.quantity_received} diff={difference}"
            chain_result = blockchain_client.flag_discrepancy(allocation.chain_allocation_id, reason)
            db.add(BlockchainTransaction(related_entity_id=allocation.id, event_type="flag_discrepancy", tx_hash=chain_result["tx_hash"]))
            blockchain_note = "flagged on-chain"
        except BlockchainNotDeployedError as exc:
            blockchain_note = f"blockchain unavailable: {exc}"
    db.commit()

    log_action(db, actor=user.username, action="discrepancy_flagged", entity_type="allocation", entity_id=allocation.id, details={"difference": difference})
    return {"allocation_id": allocation.id, "status": "DISCREPANCY", "discrepancy_id": discrepancy.id, "difference": difference, "blockchain_note": blockchain_note}


@router.get("/discrepancies")
def list_discrepancies(status_filter: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Discrepancy)
    if status_filter:
        q = q.filter(Discrepancy.status == status_filter)
    rows = q.order_by(Discrepancy.created_at.desc()).all()
    return [
        {
            "id": d.id, "allocation_id": d.allocation_id, "expected_quantity": d.expected_quantity,
            "received_quantity": d.received_quantity, "difference": d.difference,
            "reported_by": d.reported_by, "status": d.status, "resolution_note": d.resolution_note,
            "created_at": d.created_at.isoformat(),
        }
        for d in rows
    ]


@router.post("/discrepancies/resolve")
def resolve_discrepancy(
    payload: ResolveDiscrepancyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("DISTRICT_OFFICER", "AUDITOR", "SUPER_ADMIN")),
):
    discrepancy = db.query(Discrepancy).filter(Discrepancy.id == payload.discrepancy_id).first()
    if discrepancy is None:
        raise HTTPException(status_code=404, detail="Unknown discrepancy_id")

    discrepancy.status = "RESOLVED"
    discrepancy.resolution_note = payload.resolution_note
    discrepancy.resolved_at = datetime.now(timezone.utc)
    db.commit()

    log_action(db, actor=user.username, action="discrepancy_resolved", entity_type="discrepancy", entity_id=discrepancy.id, details={"resolution_note": payload.resolution_note})
    return {"discrepancy_id": discrepancy.id, "status": "RESOLVED"}
