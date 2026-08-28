from pydantic import BaseModel, Field


class RiskPredictRequest(BaseModel):
    rain_24h_mm: float = Field(..., ge=0)
    rain_72h_mm: float = Field(..., ge=0)
    rain_7d_mm: float = Field(..., ge=0)
    rain_intensity_max_mm_h: float = Field(..., ge=0)


class ImpactRequest(BaseModel):
    district: str
    risk_score: float = Field(..., ge=0, le=1)


class ReliefRequest(BaseModel):
    exposed_population: int = Field(..., ge=0)
    relief_days: int = Field(3, gt=0)


class AllocateRequest(BaseModel):
    district: str
    resource_type: str
    quantity: int = Field(..., gt=0)
    recipient_org: str


class AllocationIdRequest(BaseModel):
    allocation_id: int = Field(..., gt=0)


class FlagDiscrepancyRequest(BaseModel):
    allocation_id: int = Field(..., gt=0)
    reason: str


class LoginRequest(BaseModel):
    username: str
    password: str


class NetRequirementRequest(BaseModel):
    zone_name: str
    exposed_population: int = Field(..., ge=0)
    relief_days: int = Field(3, gt=0)
    disaster_label: str = "DEMO-SCENARIO"


class ZonePriorityRequest(BaseModel):
    zone_name: str
    risk_level: str
    population_exposed: int = Field(..., ge=0)
    gross_requirement: float = Field(..., ge=0)
    net_requirement: float = Field(..., ge=0)
    urgency: float = Field(0.5, ge=0, le=1)
    accessibility_score: float = Field(0.5, ge=0, le=1)


class ComputePrioritiesRequest(BaseModel):
    disaster_label: str = "DEMO-SCENARIO"
    zones: list[ZonePriorityRequest]


class WarehouseOptionRequest(BaseModel):
    warehouse_id: int
    resource_type: str
    distance_km: float = Field(..., ge=0)
    accessibility_score: float = Field(..., ge=0, le=1)


class ZoneDemandRequest(BaseModel):
    zone_id: int
    quantity_needed: float = Field(..., ge=0)
    priority_score: float = Field(..., ge=0)


class RecommendAllocationRequest(BaseModel):
    resource_type: str
    zones: list[ZoneDemandRequest]
    warehouses: list[WarehouseOptionRequest]


class ApproveAllocationRequest(BaseModel):
    warehouse_id: int
    zone_id: int
    resource_type: str
    quantity: float = Field(..., gt=0)
    distance_km: float = Field(..., ge=0)
    accessibility_score: float = Field(..., ge=0, le=1)
    reasoning: str
    allocation_method: str


class RecordDispatchRequest(BaseModel):
    allocation_id: int = Field(..., gt=0)
    quantity_dispatched: float = Field(..., gt=0)


class ConfirmDeliveryRequest(BaseModel):
    allocation_id: int = Field(..., gt=0)
    quantity_received: float = Field(..., ge=0)


class ResolveDiscrepancyRequest(BaseModel):
    discrepancy_id: int = Field(..., gt=0)
    resolution_note: str


class InventoryUpdateRequest(BaseModel):
    warehouse_id: int
    resource_type: str
    quantity_available: float = Field(..., ge=0)
