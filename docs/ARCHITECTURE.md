# Architecture — SETU (SIH 2026, IHSIH027)

Product name: **SETU** ("bridge") — used consistently across code, tests, and the team's
planning documents (`docs/SETU_SIH_Technical_Masterplan.md`,
`docs/SETU_Frozen_Implementation_Spec.md`). An unrelated later brief referred to the same
concept as "PARVAHA"; this build keeps SETU since renaming would touch every file for no
functional gain — flag to the team if a hard rename is actually wanted.

## 1. System architecture (as built, not as originally pitched)

```
REAL DATA (Open-Meteo / USGS / GDACS, live HTTP)
        |
        v
Feature engineering (rolling rainfall windows — app/ml/train.py)
        |
        v
AI Early Warning (LogisticRegression risk score — app/services/risk_model.py)
        |
        v
GIS Impact Assessment (population x risk x vulnerability — app/services/gis_impact.py)
        |
        v
Relief Requirement Engine (gross - existing inventory = net — app/services/requirement_engine.py)
        |
        v
Priority Engine (explainable weighted score — app/services/priority_engine.py)
        |
        v
Allocation Engine (OR-Tools LP / greedy fallback — app/services/allocation_engine.py)
        |
        v
Human approval (JWT+RBAC gated — app/api/routes/allocations.py::approve)
        |
        v
Off-chain state (SQLite: allocations/shipments/deliveries/discrepancies)
        |         \
        v          v
Blockchain mirror   Delivery verification (dispatched vs received — app/api/routes/deliveries.py)
(ReliefTracking.sol)        |
        |                   v
        +------------> Discrepancy detection -> Audit log -> GET /api/audit
```

Why each stage exists:

- **Live data over synthetic environmental data**: the whole point of an early-warning
  system is reacting to real conditions; Open-Meteo was chosen over a mock because it needs
  no API key/registration and this build environment has confirmed outbound internet access
  (see `docs/DATA_SOURCES.md`).
- **A separate Requirement Engine, not folded into the ML model**: relief-quantity decisions
  must be auditable and overridable by a human authority — a black-box model producing "send
  38,520 units" with no visible formula would fail the "why this quantity?" transparency
  requirement (Section 70 of the working spec). `requirement_engine.py` is a pure function of
  named inputs, testable in isolation (`backend/tests/test_requirement_engine.py`).
- **A separate Priority Engine**: same reasoning — a weighted, inspectable formula
  (`priority_engine.py`) rather than a second ML model, because there is no large labeled
  "correct priority ranking" dataset to train on, and the formula's terms must be individually
  explainable to a district officer deciding whether to override it.
- **Allocation as an LP (OR-Tools) with a labeled fallback**: framing allocation as a
  transportation problem (minimize effective transport cost + a priority-weighted shortage
  penalty) lets it correctly prefer an accessible-but-farther warehouse over an
  inaccessible-but-nearer one (see `test_inaccessible_warehouse_is_excluded_even_if_nearest`
  in `backend/tests/test_allocation_engine.py`) — a purely greedy nearest-warehouse rule
  cannot express that trade-off as cleanly. A greedy fallback still runs if `ortools` is
  unavailable or the LP is infeasible, and the response always states which method ran.
- **Blockchain as a mirror of lifecycle events, not the primary store**: see `BLOCKCHAIN.md`
  for the full justification — the short version is that PostgreSQL/SQLite is the
  single-party operational database, and the chain exists only for the specific
  cross-organization trust problem of the allocation lifecycle.
- **Off-chain quantity comparison before any chain write**: blockchain does not verify that
  input data is true; the backend computes dispatched-vs-received discrepancies itself and
  only then tells the chain which assertion (verified vs. discrepancy) to record.

## 2. RBAC / user-role architecture

Roles (`backend/app/auth/deps.py::ROLES`): `SUPER_ADMIN`, `DISTRICT_OFFICER`, `NGO`,
`WAREHOUSE_MANAGER`, `RELIEF_CENTRE`, `AUDITOR`, `PUBLIC`. Every protected route declares its
allowed roles explicitly via `Depends(require_role(...))` — there is no default-allow path.
Ownership checks go beyond role membership where it matters: a `WAREHOUSE_MANAGER` can only
update inventory for their own organization's warehouse
(`app/api/routes/resources.py::update_inventory`), not any warehouse in the system.

## 3. Deployment architecture (current build)

Everything runs as local processes for this prototype — see `README.md` "Running it" and
`scripts/run_demo.sh`:

```
FastAPI backend  (uvicorn, port 8000)  --- SQLite file (backend/setu.db)
Hardhat local chain (port 8545)        --- ReliefTracking.sol
Streamlit dashboard (port 8501)        --- calls the backend over HTTP
```

Production deployment (documented target, not built): containerized backend + PostgreSQL/
PostGIS + a permissioned blockchain network + a React/Next.js frontend, per
`docs/SETU_Frozen_Implementation_Spec.md` Phase 17. `DATABASE_URL` in `app/core/config.py` is
already an environment variable specifically so this swap doesn't require code changes beyond
the DB URL and adding PostGIS geometry columns.

## 4. Offline synchronization

**Not implemented in this build.** The target design (Section 30/31 of the working spec):
a field device queues transactions locally with a timestamp while offline, and syncs to the
backend (with server-side validation and conflict detection) once connectivity returns,
never claiming a blockchain transaction happened while genuinely offline. This is the
largest architectural gap between this build and the full specification — see
`LIMITATIONS.md`.

## 5. Why SQLite, not PostgreSQL/PostGIS, in this build

No local PostgreSQL instance and no running Docker daemon were available in this build
environment (Docker Desktop was installed but not started). The schema
(`backend/app/db/models.py`) is written closely enough to the frozen spec's PostgreSQL DDL
that the migration path is: point `DATABASE_URL` at a Postgres connection string, add
PostGIS geometry columns to `Zone`/future polygon tables, and reproject the geo-distance
calculation in `app/services/geo_utils.py` to `ST_Distance` on a geography column instead of
haversine. No schema redesign is required.

## 6. Region selection (why Nagaon, Assam — not Kerala)

A later brief suggested Kerala (2018 flood) as the demo region. This build keeps **Nagaon
district, Assam (Kopili sub-basin)**, per the scored comparison in
`docs/SETU_Frozen_Implementation_Spec.md` Phase 2: Nagaon/Kopili scored 93/100 vs. Kerala's
74/100, primarily because a published, reusable Sentinel-1 SAR flood-labeling methodology
already exists for that exact basin and it floods near-annually (more usable training
events than a single dominant historical event). This is a judgment call worth revisiting
with the team, not a unilateral decision to treat as final — but it reflects the more
rigorously justified existing analysis rather than defaulting to the newer brief without
reviewing why the original choice was made.
