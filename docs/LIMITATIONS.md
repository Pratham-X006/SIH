# Known Limitations — read this before claiming anything about this system

Honesty about what is NOT yet real is as important as demonstrating what is. This file is
the single place that lists every substitution, placeholder, and unimplemented item —
cross-referenced from `DATA_SOURCES.md`, `MODEL_CARD.md`, `BLOCKCHAIN.md`, and `JUDGE_QA.md`.

## Data

- **Rainfall**: Open-Meteo (global reanalysis/forecast grid) substitutes for the target
  architecture's IMD/CHIRPS gridded rainfall. Not a station-level IMD observation.
- **Population/vulnerability**: a 7-district hand-compiled sample (`data/districts_sample.json`),
  not WorldPop grid data or OSM infrastructure layers. `vulnerability_index` per district is
  a judgment-call placeholder, not a sourced statistic.
- **Flood-extent ground truth**: not implemented. The masterplan's Sentinel-1 SAR + Otsu
  thresholding methodology for Nagaon/Kopili (Google Earth Engine) is documented as the
  target approach but requires GEE registration and is not wired into this build.
- **River gauge data (CWC Kampur/Dharamtul)**: not implemented. No CWC scraping/ingestion
  exists in this codebase.
- **No real historical flood event is replayed.** `scripts/run_demo_scenario.py` uses REAL
  live rainfall at the time it's run, not a reenactment of the 2018/2020 Kopili floods.

## Machine learning

- The trained model is `scikit-learn` `LogisticRegression` on 4 rolling-rainfall features —
  not the LSTM/CNN named in the original pitch. See `MODEL_CARD.md` for the justification
  (a small, single-location historical dataset does not support a deep sequence model, and
  a simple, explainable baseline is more defensible at this data scale).
- The training label is a **documented heuristic** (top-decile 3-day rainfall), not a real
  flood-occurrence record. No public, freely-available ground-truth flood/no-flood label
  exists for arbitrary coordinates at this project's timescale.
- No formal held-out event-based test set exists yet — `train.py` does a single
  train/test split, not the event-level chronological split the frozen spec calls for.
  This is flagged, not hidden: do not present the reported classification metrics as
  final model evaluation.
- Model outputs are not currently calibrated (no Platt scaling/isotonic regression applied).

## GIS

- No PostGIS, no real polygon geometries, no road-network graph. "Zones" are point
  district centroids with a hand-set population figure — impact/exposure math is a scalar
  formula (`population × risk_score × vulnerability_index`), not a spatial overlay.
- No accessibility/road-closure feed. `accessibility_score` used by the priority and
  allocation engines is a manually-assigned ASSUMPTION per warehouse for demo purposes.

## Relief estimation

- Per-capita/per-household coefficients (`relief_estimator.py`) are rounded rules of thumb,
  not sourced from the Sphere Handbook or a specific state SDRF/NDRF relief-code document in
  this build (the masterplan names Sphere's 15L/person/day water minimum as a real citation
  to adopt — this build has not yet updated the constant to cite it directly).

## Database

- SQLite, not PostgreSQL/PostGIS. This build environment had no local Postgres instance and
  no running Docker daemon available, so the schema (`backend/app/db/models.py`) is written
  in SQLAlchemy against SQLite. Fields and relationships mirror the frozen spec's PostgreSQL
  DDL (`docs/SETU_Frozen_Implementation_Spec.md` Phase 14) closely enough that migrating
  `DATABASE_URL` to a Postgres connection string plus adding PostGIS geometry columns is the
  documented upgrade path, not a redesign.

## Blockchain

- Local Hardhat single-node development chain, not a public testnet or a permissioned
  multi-organization consortium network. See `BLOCKCHAIN.md`.
- One admin private key controls all contract calls (`ReliefTracking.sol`'s `onlyAdmin`
  modifier) — the backend's off-chain RBAC (JWT + role checks) governs who can trigger which
  API call, but the contract itself does not yet distinguish District Admin / NGO / Warehouse
  identities on-chain the way the frozen spec's Fabric MSP design intends.

## Security

- JWT secret defaults to a hardcoded dev value if `JWT_SECRET_KEY` is not set — must be
  overridden via environment variable before any non-local deployment.
- No rate limiting, no HTTPS enforcement, no secret manager integration in this build.
- CORS is wide open (`allow_origins=["*"]`) — noted inline in `main.py` as needing
  tightening before any real deployment.

## Offline mode

- Not implemented. Section 30/31's offline-first field workflow (local queueing, sync,
  conflict detection) is documented as a target architecture item but has no code yet.

## Frontend

- The dashboard is Streamlit (`dashboard/app.py`), functional and wired to every backend
  endpoint that existed before this session's additions, but not yet updated for the new
  RBAC/priority/allocation/discrepancy endpoints, and not the React/Next.js + MapLibre
  "command centre" UI described in the full spec. This is the largest remaining gap between
  this build and the full 80-section specification.

## What IS real and verified working (see session verification, not just claimed)

- Live Open-Meteo/USGS/GDACS API calls, confirmed reachable and returning real data.
- JWT auth + RBAC, confirmed: anonymous → 401, wrong role → 403, correct role → 200.
- SQLite persistence across the full schema, confirmed via direct queries.
- The priority engine, allocation engine (OR-Tools LP with a labeled greedy fallback),
  and requirement engine — all confirmed via unit tests (`backend/tests/`, 21 passing) and
  a full live run.
- The Solidity contract — 4 Hardhat tests passing, and a real local chain deployment with 6
  genuine on-chain transactions recorded during a full scenario run (verified in this
  session's own terminal output, not simulated in prose).
- End-to-end discrepancy detection: dispatched ≠ received correctly produced a DISCREPANCY
  status and a flagged on-chain event, confirmed via a real API call sequence.
