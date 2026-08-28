"""Operational database schema (SQLite for this prototype — see session.py).

This is the off-chain system of record (Section 21/26 of the spec): everything bulky,
mutable, or single-party-authoritative lives here. The blockchain (blockchain_service.py +
ReliefTracking.sol) separately records only the small, cross-organizational allocation
lifecycle events that multiple orgs need a tamper-evident shared view of — this file's
`chain_tx_hash` / `BlockchainTransaction` rows are the link between the two, not a
duplicate of one in the other.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    org_type: Mapped[str] = mapped_column(String)  # gov | ngo | warehouse
    verified: Mapped[bool] = mapped_column(default=False)

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    warehouses: Mapped[list["Warehouse"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    # SUPER_ADMIN | DISTRICT_OFFICER | NGO | WAREHOUSE_MANAGER | RELIEF_CENTRE | AUDITOR | PUBLIC
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="users")


class Zone(Base):
    """A demo "zone" = a district from data/districts_sample.json for this prototype's
    granularity. Production would use village/ward polygons in PostGIS (see ARCHITECTURE.md).
    """

    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    state: Mapped[str] = mapped_column(String)
    hazard_focus: Mapped[str] = mapped_column(String)
    lat: Mapped[float] = mapped_column()
    lon: Mapped[float] = mapped_column()


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    lat: Mapped[float] = mapped_column()
    lon: Mapped[float] = mapped_column()
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="warehouses")
    inventory: Mapped[list["ResourceInventory"]] = relationship(back_populates="warehouse")


class ResourceInventory(Base):
    __tablename__ = "resource_inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    resource_type: Mapped[str] = mapped_column(String)  # food_kg | water_litres | medical_kits | shelter_units
    quantity_available: Mapped[float] = mapped_column()
    quantity_reserved: Mapped[float] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now)

    warehouse: Mapped["Warehouse"] = relationship(back_populates="inventory")


class ReliefRequirement(Base):
    """Output of the explainable Requirement Engine (Section 17): gross - existing = net,
    computed per zone/disaster/resource_type. `assumptions_json` stores the exact multiplier
    chain so the UI can answer "why this quantity?" (Section 70)."""

    __tablename__ = "relief_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"))
    disaster_label: Mapped[str] = mapped_column(String)  # freeform event tag, e.g. "NAGAON-FLOOD-2026-08"
    resource_type: Mapped[str] = mapped_column(String)
    population_exposed: Mapped[int] = mapped_column()
    severity: Mapped[str] = mapped_column(String)  # low | moderate | high | severe
    gross_requirement: Mapped[float] = mapped_column()
    existing_inventory: Mapped[float] = mapped_column()
    net_requirement: Mapped[float] = mapped_column()
    assumptions_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=_now)


class PriorityScore(Base):
    """Output of the explainable Priority Engine (Section 18). `explanation_json` stores
    every weighted term so the UI can show the full breakdown, not just the final number."""

    __tablename__ = "priority_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"))
    disaster_label: Mapped[str] = mapped_column(String)
    severity_score: Mapped[float] = mapped_column()
    population_norm: Mapped[float] = mapped_column()
    resource_deficit_norm: Mapped[float] = mapped_column()
    urgency: Mapped[float] = mapped_column()
    accessibility_score: Mapped[float] = mapped_column()
    priority_score: Mapped[float] = mapped_column()
    explanation_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=_now)


class Allocation(Base):
    """Mirrors the on-chain allocation lifecycle (Allocated -> Dispatched -> Delivered |
    DiscrepancyFlagged, see ReliefTracking.sol) plus off-chain fields the chain doesn't
    need: the allocation engine's reasoning, and dispatched/received quantities used to
    detect discrepancies (Section 29) *before* asking the chain to record the assertion."""

    __tablename__ = "allocations"

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    resource_type: Mapped[str] = mapped_column(String)
    quantity_recommended: Mapped[float] = mapped_column()
    quantity_dispatched: Mapped[float | None] = mapped_column(nullable=True)
    quantity_received: Mapped[float | None] = mapped_column(nullable=True)
    distance_km: Mapped[float] = mapped_column()
    accessibility_score: Mapped[float] = mapped_column()
    reasoning: Mapped[str] = mapped_column(String)
    allocation_method: Mapped[str] = mapped_column(String)  # "ortools_lp" | "greedy_fallback"
    status: Mapped[str] = mapped_column(String, default="RECOMMENDED")
    # RECOMMENDED -> APPROVED -> ALLOCATED(on-chain) -> DISPATCHED -> DELIVERED -> VERIFIED
    #                                                                          -> DISCREPANCY
    chain_allocation_id: Mapped[int | None] = mapped_column(nullable=True)
    chain_tx_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_now)
    approved_at: Mapped[datetime | None] = mapped_column(nullable=True)
    dispatched_at: Mapped[datetime | None] = mapped_column(nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(nullable=True)

    discrepancy: Mapped["Discrepancy | None"] = relationship(back_populates="allocation", uselist=False)


class Discrepancy(Base):
    """Created automatically when dispatched != received (Section 29). Human-resolved only —
    the system never silently overwrites either quantity (Section 28)."""

    __tablename__ = "discrepancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    allocation_id: Mapped[int] = mapped_column(ForeignKey("allocations.id"), unique=True)
    expected_quantity: Mapped[float] = mapped_column()
    received_quantity: Mapped[float] = mapped_column()
    difference: Mapped[float] = mapped_column()
    reported_by: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="OPEN")  # OPEN | UNDER_REVIEW | RESOLVED
    resolution_note: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_now)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)

    allocation: Mapped["Allocation"] = relationship(back_populates="discrepancy")


class BlockchainTransaction(Base):
    """Fast-query mirror of on-chain events, written whenever the backend successfully
    submits a transaction via blockchain_service.py. The chain itself remains the source of
    truth (Section 21 note); this table exists only so the audit/dashboard API doesn't need
    to hit the chain RPC for every list view."""

    __tablename__ = "blockchain_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    related_entity_type: Mapped[str] = mapped_column(String, default="allocation")
    related_entity_id: Mapped[int] = mapped_column()
    event_type: Mapped[str] = mapped_column(String)  # allocate | dispatch | confirm_delivery | flag_discrepancy
    tx_hash: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(default=_now)


class AuditLog(Base):
    """Internal app-level audit trail (Section 53) for actions that are not already covered
    by the blockchain's own immutable event log (login, inventory edits, role changes,
    model deployment, data ingestion — none of which are cross-org trust problems)."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    entity_type: Mapped[str | None] = mapped_column(String, nullable=True)
    entity_id: Mapped[int | None] = mapped_column(nullable=True)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(default=_now)


class DataSource(Base):
    """Machine-readable mirror of docs/DATA_SOURCES.md, served via GET /api/data-sources so
    the frontend can render REAL/DERIVED/SYNTHETIC/SIMULATED provenance badges (Section 72)
    next to whatever number came from that source, instead of hand-waving "the data is real"."""

    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    category: Mapped[str] = mapped_column(String)  # REAL | DERIVED | SYNTHETIC | SIMULATED
    source: Mapped[str] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    temporal_coverage: Mapped[str] = mapped_column(String)
    spatial_coverage: Mapped[str] = mapped_column(String)
    resolution: Mapped[str] = mapped_column(String)
    variables: Mapped[str] = mapped_column(String)
    processing: Mapped[str] = mapped_column(String)
    license: Mapped[str] = mapped_column(String)
    limitations: Mapped[str] = mapped_column(String)


class ModelVersion(Base):
    """Versioning record for the risk model (Section 44). One row per `train.py` run."""

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[str] = mapped_column(String, default="flood-risk-logreg")
    version: Mapped[str] = mapped_column(String)
    algorithm: Mapped[str] = mapped_column(String)
    training_data_source: Mapped[str] = mapped_column(String)
    feature_names_json: Mapped[list] = mapped_column(JSON)
    metrics_json: Mapped[dict] = mapped_column(JSON)
    artifact_path: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=_now)
