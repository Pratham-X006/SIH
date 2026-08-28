# Judge Q&A — SETU (SIH 2026, IHSIH027)

Answers reflect what is actually implemented and verified in this codebase, cross-referenced
to the file or doc that backs each claim. Where something is not built, that's stated
directly, with the reason and the documented future path — see `LIMITATIONS.md` for the
consolidated list.

**1. What exact problem are you solving?**
The gap between "a hazard forecast exists" and "a coordinated, measurable, trustworthy
relief response happens." Official agencies (CWC/IMD/NRSC) already forecast hazards; nobody
provides one pipeline from that forecast to "which zone, needs what, from where, verifiably
delivered." See `docs/SETU_SIH_Technical_Masterplan.md` Section 2.

**2. Why can't existing systems solve it?**
NDMA's SACHET disseminates alerts but doesn't compute affected population or relief
logistics; CWC/C-FLOOD forecasts river levels but doesn't do impact assessment or
allocation; Bhuvan-Disaster maps floods post-event, not pre-event impact. None of them close
the loop to verified delivery. Full gap analysis: masterplan Section 3.

**3. Why AI?**
To turn raw rainfall into a single, gradable risk number per location/horizon, rather than
requiring a human to manually cross-reference multiple rainfall bulletins. See `MODEL_CARD.md`.

**4. Why LSTM?**
We did NOT use an LSTM. `MODEL_CARD.md` explains why: too little single-location historical
data to justify a deep sequence model over an interpretable logistic regression on rolling-
window features at this project's current data scale. LSTM/XGBoost remain the documented
upgrade path once more historical data is aggregated.

**5. Why CNN, if used?**
Not used, and not planned unless genuinely gridded spatial inputs (e.g., DEM/satellite
patches) are added — using a CNN "because the brief said AI" would be exactly the kind of
technology-checklist mistake this project explicitly avoids (masterplan Section 7.1).

**6. What exactly is predicted?**
A rainfall-based risk score (0-1) and a risk_level bucket (low/moderate/high/severe) for a
location, from 4 rolling-rainfall features. Not "floods will happen" — see `MODEL_CARD.md`
for the precise, honest framing.

**7. What happens when the AI is wrong?**
The system never auto-issues warnings or auto-allocates resources off a prediction alone —
every allocation requires human approval (`app/api/routes/allocations.py::approve`, enforced
by RBAC). If no trained model exists, the API falls back to a labeled heuristic rule
(`"fallback_threshold_rule_untrained"`) rather than failing silently or refusing to respond.

**8. How do you handle false negatives?**
`class_weight="balanced"` is used specifically because missing a real elevated-risk period
is costlier than a false alarm. No minimum-recall threshold tuning exists yet — flagged
honestly in `MODEL_CARD.md` as unresolved, not hidden.

**9. How do you generate flood extent?**
We do not. This build has no satellite-derived flood-extent pipeline (Sentinel-1/GEE) —
the target methodology is documented in the masterplan for the Nagaon/Kopili basin
specifically, but not implemented. See `LIMITATIONS.md`.

**10. How do you estimate population exposure?**
`estimated_exposed_population = population × risk_score × vulnerability_index`, capped at
100%, always labeled ESTIMATED (`app/services/gis_impact.py`). Population/vulnerability
figures are a hand-compiled sample dataset, not WorldPop grid data — see `DATA_SOURCES.md`.

**11. How do you calculate relief requirements?**
`gross_requirement = population × per-capita/per-household coefficient × days`, then
`net_requirement = gross_requirement − existing_inventory` (summed from real seeded
warehouse stock). Formula and coefficients: `app/services/relief_estimator.py` +
`app/services/requirement_engine.py`. Every API response includes the assumptions used.

**12. Why did Zone A get Priority 1?**
`priority_score = 0.3×severity + 0.25×population_norm + 0.25×resource_deficit_norm +
0.1×urgency + 0.1×(1−accessibility)` — every term and its numeric contribution is returned
in the API response's `explanation` field (`app/services/priority_engine.py`), not just the
final number. Verified live in `scripts/run_demo_scenario.py`'s Step 4 output.

**13. How do you choose a warehouse?**
An OR-Tools linear program minimizes effective transport cost (distance ÷ accessibility) plus
a priority-weighted shortage penalty, with any warehouse below an accessibility threshold
excluded outright regardless of distance (`app/services/allocation_engine.py`). Test proving
"nearer-but-inaccessible loses to farther-but-accessible":
`backend/tests/test_allocation_engine.py::test_inaccessible_warehouse_is_excluded_even_if_nearest`.

**14. What if roads are inaccessible?**
`accessibility_score` per warehouse (currently a manually-assigned ASSUMPTION — no live
road-closure feed, see `LIMITATIONS.md`) drives both exclusion (below threshold) and cost
weighting (above threshold) in the allocation LP.

**15. Why blockchain?**
Multiple independent organizations (district admin, NGOs, warehouses) don't fully trust
each other's private records; a shared tamper-evident log of the allocation lifecycle
addresses that specific problem. Full reasoning: `BLOCKCHAIN.md`.

**16. Why not PostgreSQL [for the blockchain's job]?**
PostgreSQL is exactly what's used for everything that ISN'T a cross-organization trust
problem (inventory, GIS, predictions, priority scores) — see `BLOCKCHAIN.md` "Why NOT
PostgreSQL for everything." Blockchain is additive, not a replacement database.

**17. What goes on-chain?**
Allocation id, district, resource type, quantity, allocator address, recipient org,
timestamp, status. No PII, no GIS geometry, no model internals. `ReliefTracking.sol`.

**18. What stays off-chain?**
User accounts, full allocation reasoning, requirement/priority calculations, discrepancy
detail and resolution notes, the audit log. `backend/app/db/models.py`.

**19. Who validates transactions?**
Off-chain: JWT + RBAC (`app/auth/deps.py`) gates who can call which API endpoint, and
ownership checks (e.g., a warehouse manager can only edit their own org's inventory) go
beyond role membership. On-chain: the contract's `onlyAdmin` modifier restricts every
state-changing call to one authorized signer in this build (see `BLOCKCHAIN.md` — per-org
on-chain identity is documented future scope, not yet implemented).

**20. What prevents false information entering blockchain?**
Nothing on-chain does, by design — blockchain doesn't verify truth, it makes recorded
assertions tamper-evident after the fact. Truth-checking happens off-chain: dispatched vs.
received quantities are compared by the backend before any chain write
(`app/api/routes/deliveries.py::confirm_delivery`), and a mismatch produces a
DISCREPANCY status plus an audit-logged flag rather than silently accepting either number.

**21. What happens without internet?**
Not implemented in this build (see `LIMITATIONS.md` — offline mode is the largest
documented gap). Target design: local queueing with timestamps, sync + conflict detection on
reconnect, never claiming a blockchain transaction happened while genuinely offline.

**22. What happens if AI fails?**
Falls back to a labeled heuristic (`fallback_threshold_rule_untrained`) rather than
returning an error or a silent wrong answer — verified via `GET /api/system/status` and
`app/services/risk_model.py`.

**23. What happens if blockchain fails?**
Verified in this session: allocation/dispatch/delivery status transitions proceed off-chain
regardless of chain availability, and the API response states plainly
("blockchain unavailable... relief operations may proceed") rather than blocking the
workflow. `GET /api/system/status` also reports blockchain readiness separately.

**24. How do you prevent duplicate claims?**
Not implemented in this build. No beneficiary/household identifier or duplicate-claim check
exists yet — documented as future scope (the frozen spec's Section 32 design: check for an
existing equivalent claim before confirming distribution, without putting PII on-chain).

**25. How does the system scale?**
Not load-tested. Architecturally: the FastAPI backend, ML inference, and allocation engine
are stateless services that could scale horizontally behind a load balancer; SQLite would
need to become PostgreSQL first (documented migration path in `ARCHITECTURE.md`); the
blockchain would need to become a real multi-node network. None of this has been built or
benchmarked — stated as a target, not a demonstrated capability.

**26. Who uses the platform?**
District disaster officers (approve/override), NGOs (dispatch/verify), warehouse managers
(inventory), relief centres (confirm receipt/flag discrepancies), auditors (read-only audit
trail), and the public (aggregate, non-PII view). RBAC roles: `app/auth/deps.py::ROLES`.

**27. Who operates it?**
In production, a district/state disaster management authority would operate the backend and
database; NGOs and warehouses would run their own accounts, not their own infrastructure.
Not applicable to this prototype — no real deployment exists.

**28. How does it integrate with existing government systems?**
It doesn't yet — this build has no NDMA/SDMA/CWC/IMD API integration. Designed as an
integration layer, not a replacement, per masterplan Section 3; actual integration would
require a data-sharing arrangement with those agencies (future work, not claimed as done).

**29. What data is real vs. synthetic?**
Full breakdown with REAL/DERIVED/SYNTHETIC/SIMULATED labels: `DATA_SOURCES.md`. Short
version: live weather/seismic/hazard feeds are real; population/vulnerability figures are a
derived sample, not WorldPop/Census-grid data; all warehouses/inventory/allocations/
deliveries are synthetic prototype data generated by `scripts/seed_demo.py` and
`scripts/run_demo_scenario.py`; the local blockchain's mechanics are real, its network is a
local simulation of a production consortium chain.

**30. What happens after SIH?**
Documented, not promised: real government/CWC/IMD data-sharing discussions; PostgreSQL/
PostGIS migration; a real road-network accessibility feed; Sentinel-1 flood-extent labeling
for the Nagaon/Kopili basin; a permissioned multi-organization blockchain network; offline
field-mode; a React/Next.js command-centre frontend. None of these are claimed as built —
see `LIMITATIONS.md` for the complete, current gap list.
