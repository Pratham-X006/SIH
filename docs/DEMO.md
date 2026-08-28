# Demo Guide — SETU

## One-time setup

```bash
# Backend deps (use a venv OUTSIDE any OneDrive-synced folder to avoid sync slowdowns)
cd backend
python -m venv /path/outside/onedrive/venv
/path/outside/onedrive/venv/bin/pip install -r requirements.txt   # or Scripts\pip.exe on Windows

# Blockchain deps
cd ../blockchain
npm install
```

## Every time you demo (4 terminals, or use scripts/run_demo.sh for git-bash/WSL/macOS/Linux)

```bash
# Terminal 1 — local blockchain
cd blockchain
npx hardhat node

# Terminal 2 — deploy the contract (after Terminal 1 says "Started ... JSON-RPC server")
cd blockchain
npx hardhat run scripts/deploy.js --network localhost

# Terminal 3 — backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 4 — seed data, then run the scenario
python scripts/seed_demo.py
python scripts/run_demo_scenario.py

# Optional — dashboard
cd dashboard && streamlit run app.py
```

Or, from a POSIX shell (git-bash on Windows works): `bash scripts/run_demo.sh` does
Terminals 1-2-3-4 for you and leaves the backend/chain running in the background.

## What the scenario demonstrates (`scripts/run_demo_scenario.py`)

Every step below is a real HTTP call against the running API — nothing is pre-scripted output.

1. **PREDICT** — fetches real live rainfall for Nagaon, Assam from Open-Meteo, runs it
   through the risk model.
2. **ASSESS** — GIS impact assessment for Nagaon vs. a comparison zone (Kamrup).
3. **ESTIMATE** — relief requirement engine: gross requirement minus real seeded warehouse
   inventory = net requirement, per resource type.
4. **PRIORITIZE** — computes and prints the full weighted-term breakdown for why Nagaon
   outranks the comparison zone.
5. **ALLOCATE** — recommends warehouse-to-zone shipments via OR-Tools, explicitly excluding
   an intentionally-modeled low-accessibility warehouse and explaining every line item.
6. **Approve → dispatch → confirm (matched quantities)** → ends **VERIFIED**, with a real
   on-chain transaction if the blockchain is running (gracefully proceeds off-chain-only if not).
7. **Approve → dispatch → confirm (mismatched quantities, intentional)** → ends
   **DISCREPANCY**, with the mismatch computed off-chain before the chain is told to record it.
8. **AUDIT** — lists real on-chain transaction hashes and the open discrepancy record.

The discrepancy is left `OPEN` on purpose — resolve it live during the demo via
`POST /api/deliveries/discrepancies/resolve` as the `auditor` or `district_officer` user to
show that flow too.

## Demo login credentials (SYNTHETIC, seeded by `scripts/seed_demo.py`)

| Username | Password | Role |
|---|---|---|
| district_officer | demo-pass-1 | DISTRICT_OFFICER |
| warehouse_mgr | demo-pass-2 | WAREHOUSE_MANAGER |
| ngo_coordinator | demo-pass-3 | NGO |
| relief_centre | demo-pass-4 | RELIEF_CENTRE |
| auditor | demo-pass-5 | AUDITOR |
| admin | demo-pass-0 | SUPER_ADMIN |

## If something looks wrong mid-demo

- `GET /api/system/status` shows database/ML/blockchain readiness at a glance.
- If the blockchain node isn't running, allocations still work — they proceed
  ALLOCATED/DISPATCHED/VERIFIED off-chain and the API response says so explicitly
  ("blockchain unavailable... relief operations may proceed"). This is intentional
  graceful degradation, not a bug — say so if a judge notices it.
- If `python scripts/prepare_demo.py` reports a WARN, read the detail line — it explains
  exactly what's missing and how to fix it before going live.
