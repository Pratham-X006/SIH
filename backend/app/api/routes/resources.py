from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import require_role
from app.db.models import ResourceInventory, User, Warehouse
from app.db.session import get_db
from app.models.schemas import InventoryUpdateRequest, NetRequirementRequest
from app.services.audit import log_action
from app.services.requirement_engine import compute_net_requirements

router = APIRouter(prefix="/api", tags=["resources"])


@router.get("/warehouses")
def list_warehouses(db: Session = Depends(get_db)):
    warehouses = db.query(Warehouse).all()
    return [
        {
            "id": w.id,
            "name": w.name,
            "org_id": w.org_id,
            "lat": w.lat,
            "lon": w.lon,
            "inventory": [
                {
                    "resource_type": i.resource_type,
                    "quantity_available": i.quantity_available,
                    "quantity_reserved": i.quantity_reserved,
                }
                for i in w.inventory
            ],
        }
        for w in warehouses
    ]


@router.get("/inventory")
def list_inventory(db: Session = Depends(get_db)):
    return [
        {
            "warehouse_id": i.warehouse_id,
            "resource_type": i.resource_type,
            "quantity_available": i.quantity_available,
            "quantity_reserved": i.quantity_reserved,
            "updated_at": i.updated_at.isoformat(),
        }
        for i in db.query(ResourceInventory).all()
    ]


@router.post("/inventory/update")
def update_inventory(
    payload: InventoryUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("WAREHOUSE_MANAGER", "SUPER_ADMIN")),
):
    """WAREHOUSE_MANAGER may only update inventory for their own organization's warehouse
    (Section 52: role permission is not enough, resource ownership must also be checked)."""
    warehouse = db.query(Warehouse).filter(Warehouse.id == payload.warehouse_id).first()
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Unknown warehouse_id")
    if user.role == "WAREHOUSE_MANAGER" and warehouse.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Cannot modify inventory for another organization's warehouse")

    row = (
        db.query(ResourceInventory)
        .filter(ResourceInventory.warehouse_id == payload.warehouse_id, ResourceInventory.resource_type == payload.resource_type)
        .first()
    )
    old_qty = row.quantity_available if row else None
    if row is None:
        row = ResourceInventory(warehouse_id=payload.warehouse_id, resource_type=payload.resource_type, quantity_available=payload.quantity_available)
        db.add(row)
    else:
        row.quantity_available = payload.quantity_available
    db.commit()

    log_action(
        db, actor=user.username, action="inventory_update", entity_type="resource_inventory", entity_id=row.id,
        details={"warehouse_id": payload.warehouse_id, "resource_type": payload.resource_type, "old_quantity": old_qty, "new_quantity": payload.quantity_available},
    )
    return {"status": "updated", "warehouse_id": payload.warehouse_id, "resource_type": payload.resource_type, "quantity_available": payload.quantity_available}


@router.post("/requirements/calculate")
def calculate_requirements(payload: NetRequirementRequest, db: Session = Depends(get_db)):
    """Sums existing inventory across ALL warehouses (no zone-to-warehouse mapping is stored
    in this prototype) as the 'existing local inventory' offset. See requirement_engine.py."""
    rows = db.query(ResourceInventory).all()
    existing: dict[str, float] = {}
    for r in rows:
        existing[r.resource_type] = existing.get(r.resource_type, 0.0) + r.quantity_available

    results = compute_net_requirements(payload.exposed_population, payload.relief_days, existing)
    return {
        "zone_name": payload.zone_name,
        "disaster_label": payload.disaster_label,
        "requirements": [r.__dict__ for r in results],
    }
