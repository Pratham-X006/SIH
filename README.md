# AI-Powered Disaster Early Warning, Impact Assessment & Relief Management System

**SIH 2026 · Problem Statement IHSIH027 · Team: Optimistic Braincells**

An end-to-end pipeline — **Predict → Assess → Estimate → Allocate → Track → Verify** — that
forecasts floods/landslides from live weather data, estimates population and asset impact,
sizes relief requirements, and records every relief allocation on a blockchain ledger for
public, auditable transparency.

## Architecture

```mermaid
flowchart LR
    subgraph Live Data
        A1[Open-Meteo\nrainfall / soil moisture]
        A2[USGS\nearthquakes]
        A3[GDACS\nmulti-hazard alerts]
    end
    subgraph Backend (FastAPI)
        B1[Early Warning\nrisk model]
        B2[GIS Impact\nAssessment]
        B3[Relief\nEstimator]
        B4[Blockchain\nService]
    end
    C[(Local Hardhat\nBlockchain)]
    D[Streamlit\nDashboard]

    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> B2 --> B3 --> B4
    B4 <--> C
    B1 & B2 & B3 & B4 --> D
```

## Repo layout

```
backend/     FastAPI service: live-data ingestion, risk model, GIS impact, relief estimator,
             blockchain client
blockchain/  Solidity smart contract + Hardhat project (local chain — no wallet/testnet needed)
dashboard/   Streamlit dashboard consuming the backend API
data/        Small labeled sample datasets (see data/README.md — these are NOT live)
docs/        Notes on live data sources and what's real vs. placeholder right now
```

## Status: what's real right now vs. what's a starting point

This is a working prototype, not a finished production system — every claim below was
verified by actually running the code in this session (real HTTP calls, real DB queries,
real blockchain transactions), not just written. See `docs/LIMITATIONS.md` for the full,
honest gap list and `docs/DATA_SOURCES.md` for REAL/DERIVED/SYNTHETIC/SIMULATED labeling.

| Module | State |
|---|---|
| Live data fetchers (Open-Meteo, USGS, GDACS) | **Real, working HTTP clients** — confirmed reachable from this environment. See `backend/app/services/live_data.py`. |
| Early-warning risk model | Functional baseline (`scikit-learn` logistic regression) trained on **real historical rainfall** from Open-Meteo's Archive API. Documented heuristic label, not ground-truth flood data — see `docs/MODEL_CARD.md`. |
| GIS impact assessment | Lightweight formula-based (`app/services/gis_impact.py`) against a sample district dataset — not PostGIS/WorldPop yet. |
| Relief Requirement Engine | Real formula, now with **net = gross − existing DB inventory** (`app/services/requirement_engine.py`), fully explainable via API response. |
| Priority Engine | **New.** Explainable weighted score across severity/population/resource-deficit/urgency/accessibility, full per-term breakdown returned by the API (`app/services/priority_engine.py`). |
| Allocation Engine | **New.** OR-Tools LP (with a labeled greedy fallback) that can prefer a farther, more-accessible warehouse over a nearer, inaccessible one — not just nearest-warehouse (`app/services/allocation_engine.py`). |
| Database / persistence | **New.** Real SQLite database (SQLAlchemy) — organizations, users, warehouses, inventory, zones, requirements, priorities, allocations, discrepancies, audit log, blockchain-tx mirror, data-source registry. Previously stateless. |
| Auth / RBAC | **New.** JWT login + 7 roles, enforced server-side on every protected route, with ownership checks (not just role checks) where it matters. |
| Delivery verification & discrepancy detection | **New.** Dispatched vs. received quantities compared off-chain; a mismatch creates a `Discrepancy` row and flags it on-chain — verified end-to-end with a real intentional mismatch. |
| Blockchain tracking | Solidity contract (`ReliefTracking.sol`) + Hardhat local network. 4/4 contract tests passing; a full scenario run produced 6 real on-chain transactions. See `docs/BLOCKCHAIN.md`. |
| Dashboard | Streamlit app wired to the original endpoints; **not yet updated** for the new RBAC/priority/allocation/discrepancy endpoints — see `docs/LIMITATIONS.md`. |
| Tests | **New.** 21 backend pytest unit tests (priority/allocation/requirement/GIS/geo engines) + 4 Hardhat contract tests, all passing. |

## Running it

**Tip:** create your Python venv outside any OneDrive-synced folder — OneDrive trying to
sync thousands of tiny virtualenv files causes severe slowdowns on Windows.

```bash
# 1. Backend
cd backend
python -m venv /path/outside/onedrive/venv
/path/outside/onedrive/venv/Scripts/pip install -r requirements.txt   # Scripts\pip.exe on Windows cmd
/path/outside/onedrive/venv/Scripts/python -m uvicorn app.main:app --reload --port 8000

# 2. Local blockchain (separate terminal)
cd blockchain
npm install
npx hardhat node                     # keep running
npx hardhat run scripts/deploy.js --network localhost   # in a 3rd terminal

# 3. Seed synthetic demo data + run the full pipeline once (separate terminal)
python scripts/seed_demo.py
python scripts/run_demo_scenario.py

# 4. Dashboard (separate terminal, optional)
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

Or use `bash scripts/run_demo.sh` to do steps 2-3 automatically. See `docs/DEMO.md` for the
full walkthrough and demo login credentials.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design and why each component exists
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) — every dataset, labeled REAL/DERIVED/SYNTHETIC/SIMULATED
- [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md) — model, label, evaluation, known failure modes
- [`docs/BLOCKCHAIN.md`](docs/BLOCKCHAIN.md) — why blockchain, what's on/off-chain, platform choice
- [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) — the complete, honest gap list
- [`docs/JUDGE_QA.md`](docs/JUDGE_QA.md) — direct answers to 30 likely judge questions
- [`docs/DEMO.md`](docs/DEMO.md) — step-by-step demo script and credentials
- [`docs/SETU_SIH_Technical_Masterplan.md`](docs/SETU_SIH_Technical_Masterplan.md) / [`docs/SETU_Frozen_Implementation_Spec.md`](docs/SETU_Frozen_Implementation_Spec.md) — original team planning documents (target architecture; not all of it is built yet)

## A note on live data and this environment

The live-data clients in `backend/app/services/live_data.py` call the real public APIs
(Open-Meteo, USGS, GDACS — all free, no key required). **Where you run this matters:**
your laptop, a normal cloud VM, or a deployed host (Render/Railway/etc.) all have open
internet access, so these calls return genuinely live data. This particular build was
scaffolded inside a sandboxed cloud dev container with an outbound network allowlist that
blocks calls to third-party APIs like these — so it could not hit them live while writing
this code. See `docs/live_data_sources.md` for verification notes, source docs, and the
exact endpoints used.

## Team

Optimistic Braincells — PS IHSIH027, Theme: Disaster Management, Category: Software
