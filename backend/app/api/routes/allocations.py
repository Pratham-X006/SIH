from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import require_role
from app.db.models import Allocation, BlockchainTransaction, ResourceInventory, User, Warehouse, Zone
from app.db.session import get_db
from app.models.schemas import ApproveAllocationRequest, RecommendAllocationRequest
from app.services.allocation_engine import WarehouseOption, ZoneDemand, recommend_allocation
from app.services.audit import log_action
from app.services.blockchain_service import BlockchainNotDeployedError, blockchain_client

router = APIRouter(prefix="/api/allocations", tags=["allocations"])


@router.post("/recommend")
def recommend(
    payload: RecommendAllocationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("DISTRICT_OFFICER", "SUPER_ADMIN")),
):
    """Produces a recommendation only — nothing is written to the database or the blockchain
    here. A human authority must call /approve next (Section 19/69: human-in-the-loop).

    Stock is looked up from the database, never trusted from the request body — a caller
    claiming a warehouse has more stock than it actually does must not be able to influence
    the recommendation."""
    zones = []
    for z in payload.zones:
        zone = db.query(Zone).filter(Zone.id == z.zone_id).first()
        zones.append(ZoneDemand(zone_id=z.zone_id, zone_name=zone.name if zone else str(z.zone_id), quantity_needed=z.quantity_needed, priority_score=z.priority_score))

    warehouses = []
    for w in payload.warehouses:
        warehouse = db.query(Warehouse).filter(Warehouse.id == w.warehouse_id).first()
        if warehouse is None:
            continue
        inventory_row = (
            db.query(ResourceInventory)
            .filter(ResourceInventory.warehouse_id == w.warehouse_id, ResourceInventory.resource_type == payload.resource_type)
            .first()
        )
        stock = (inventory_row.quantity_available - inventory_row.quantity_reserved) if inventory_row else 0.0
        warehouses.append(WarehouseOption(warehouse_id=w.warehouse_id, warehouse_name=warehouse.name, stock_available=max(0.0, stock), distance_km=w.distance_km, accessibility_score=w.accessibility_score))

    result = recommend_allocation(payload.resource_type, zones, warehouses)
    return {
        "resource_type": result.resource_type,
        "method": result.method,
        "lines": [line.__dict__ for line in result.lines],
        "unmet_demand": result.unmet_demand,
        "excluded_warehouses": result.excluded_warehouses,
    }


@router.post("/approve")
def approve(
    payload: ApproveAllocationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("DISTRICT_OFFICER", "SUPER_ADMIN")),
):
    """Human-in-the-loop approval gate (Section 69). Only after this call does an allocation
    get written on-chain — the recommendation endpoint above never touches the ledger."""
    warehouse = db.query(Warehouse).filter(Warehouse.id == payload.warehouse_id).first()
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Unknown warehouse_id")

    # Off-chain status (Section 31: relief operations must continue even if the blockchain
    # is unreachable) advances to ALLOCATED as soon as a human approves it — this is the
    # operational source-of-truth transition. The blockchain write below is a best-effort
    # tamper-evident mirror of that decision, not a precondition for the workflow to proceed.
    allocation = Allocation(
        zone_id=payload.zone_id,
        warehouse_id=payload.warehouse_id,
        resource_type=payload.resource_type,
        quantity_recommended=payload.quantity,
        distance_km=payload.distance_km,
        accessibility_score=payload.accessibility_score,
        reasoning=payload.reasoning,
        allocation_method=payload.allocation_method,
        status="ALLOCATED",
        approved_by=user.username,
        approved_at=None,
    )
    db.add(allocation)
    db.commit()
    db.refresh(allocation)

    try:
        chain_result = blockchain_client.allocate(
            district=str(payload.zone_id), resource_type=payload.resource_type,
            quantity=int(payload.quantity), recipient_org=warehouse.name,
        )
        allocation.chain_allocation_id = chain_result["allocation_id"]
        allocation.chain_tx_hash = chain_result["tx_hash"]
        db.add(BlockchainTransaction(related_entity_id=allocation.id, event_type="allocate", tx_hash=chain_result["tx_hash"]))
        db.commit()
        blockchain_note = "Recorded on-chain."
    except BlockchainNotDeployedError as exc:
        blockchain_note = (
            f"Allocation is ALLOCATED off-chain and relief operations may proceed "
            f"(Section 31 graceful degradation); the blockchain mirror was NOT written "
            f"because it is currently unavailable: {exc}"
        )

    log_action(db, actor=user.username, action="allocation_approve", entity_type="allocation", entity_id=allocation.id, details={"blockchain_note": blockchain_note})

    return {"allocation_id": allocation.id, "status": allocation.status, "chain_tx_hash": allocation.chain_tx_hash, "blockchain_note": blockchain_note}


@router.get("")
def list_allocations(db: Session = Depends(get_db)):
    rows = db.query(Allocation).order_by(Allocation.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "zone_id": a.zone_id,
            "warehouse_id": a.warehouse_id,
            "resource_type": a.resource_type,
            "quantity_recommended": a.quantity_recommended,
            "quantity_dispatched": a.quantity_dispatched,
            "quantity_received": a.quantity_received,
            "status": a.status,
            "allocation_method": a.allocation_method,
            "chain_tx_hash": a.chain_tx_hash,
            "created_at": a.created_at.isoformat(),
        }
        for a in rows
    ]


@router.get("/{allocation_id}")
def get_allocation(allocation_id: int, db: Session = Depends(get_db)):
    a = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if a is None:
        raise HTTPException(status_code=404, detail="Unknown allocation_id")
    return {
        "id": a.id, "zone_id": a.zone_id, "warehouse_id": a.warehouse_id, "resource_type": a.resource_type,
        "quantity_recommended": a.quantity_recommended, "quantity_dispatched": a.quantity_dispatched,
        "quantity_received": a.quantity_received, "status": a.status, "reasoning": a.reasoning,
        "allocation_method": a.allocation_method, "chain_tx_hash": a.chain_tx_hash,
        "discrepancy": None if a.discrepancy is None else {
            "id": a.discrepancy.id, "expected_quantity": a.discrepancy.expected_quantity,
            "received_quantity": a.discrepancy.received_quantity, "difference": a.discrepancy.difference,
            "status": a.discrepancy.status,
        },
    }
