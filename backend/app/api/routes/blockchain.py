from fastapi import APIRouter, HTTPException

from app.models.schemas import AllocateRequest, AllocationIdRequest, FlagDiscrepancyRequest
from app.services.blockchain_service import BlockchainNotDeployedError, blockchain_client

router = APIRouter(prefix="/blockchain", tags=["blockchain"])


def _wrap(fn, *args):
    try:
        return fn(*args)
    except BlockchainNotDeployedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/status")
def status():
    return {"ready": blockchain_client.is_ready}


@router.post("/allocate")
def allocate(payload: AllocateRequest):
    return _wrap(
        blockchain_client.allocate,
        payload.district,
        payload.resource_type,
        payload.quantity,
        payload.recipient_org,
    )


@router.post("/dispatch")
def dispatch(payload: AllocationIdRequest):
    return _wrap(blockchain_client.mark_dispatched, payload.allocation_id)


@router.post("/confirm-delivery")
def confirm_delivery(payload: AllocationIdRequest):
    return _wrap(blockchain_client.confirm_delivery, payload.allocation_id)


@router.post("/flag-discrepancy")
def flag_discrepancy(payload: FlagDiscrepancyRequest):
    return _wrap(blockchain_client.flag_discrepancy, payload.allocation_id, payload.reason)


@router.get("/ledger")
def ledger():
    return _wrap(blockchain_client.get_ledger)
