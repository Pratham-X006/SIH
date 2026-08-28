# SETU — Frozen Implementation Specification
## From Masterplan to Buildable MVP (SIH 2026, IHSIH027)

This document assumes the masterplan (architecture, model comparisons, blockchain comparison, PRD) as the accepted baseline. Nothing here re-argues those decisions. Everything here is a **frozen, specific answer** your team can build from tomorrow morning. Anything genuinely unresolved is marked **OPEN DECISION** with the minimum experiment needed to close it.

---

# PHASE 1 — MVP FREEZE: NO SCOPE CREEP

## Hazard: **FLOOD ONLY**

## Pipeline (frozen):
```
Historical/Replayed Data → Flood Risk Prediction → GIS Impact Assessment
→ Relief Requirement Estimation → Resource Allocation → Blockchain Recording
→ Delivery Verification → Dashboard
```

### INCLUDED IN MVP
- Single district, single hazard (riverine flood), single river reach/gauge as primary signal
- XGBoost/LightGBM risk model, trained on real historical data, chronological split
- GIS overlay: population-at-risk, infrastructure exposure, priority score — computed on real data
- Rule-based relief estimation formula (Sphere-informed)
- Simple assignment-optimization allocation (OR-Tools LP, not VRP)
- Blockchain: permissioned Fabric **if team can stand up a 3-org test network in time**, else Solidity/Hardhat local testnet (decision gate in Phase 11)
- Delivery verification: simulated GPS + photo hash + simulated OTP (real hashing/storage logic, simulated device inputs)
- 3 dashboards: Government (full), NGO (scoped), Public (aggregate read-only)
- Human-in-the-loop approval gate before any allocation is written on-chain

### NOT INCLUDED IN MVP
- Multi-hazard (landslide/cyclone/extreme weather)
- Multi-district / state-wide view
- Real SMS gateway at production volume (sandbox/mock acceptable)
- Vehicle Routing Problem (multi-stop route optimization)
- Real IoT sensor network
- Live NDMA/SDMA system integration (mock API endpoint only)
- Mobile-native offline-first app with full CRDT sync (basic offline queue is enough)
- Production-grade key management / HSM

### FUTURE SCOPE
- All of the above "NOT INCLUDED" items, post-hackathon, phased by the roadmap in the masterplan (Part 29).

**No new modules get added to this list. If a team member wants to add something, it goes in FUTURE SCOPE, not MVP.**

---

# PHASE 2 — FINAL DEMO GEOGRAPHY

## Candidate comparison

| Criterion (max pts) | Mahanadi Delta, Odisha (e.g. Kendrapara/Jagatsinghpur) | Kopili sub-basin, Brahmaputra system — **Nagaon district, Assam** | Periyar basin, Kerala (Ernakulam/Alappuzha) |
|---|---|---|---|
| CWC station availability (10) | 8 — Mahanadi Division stations well established, Naraj/Mundali gauges | 9 — CWC gauges at Kampur & Dharamtul directly on Kopili, plus broader Brahmaputra network (Neamatighat etc.) | 7 — fewer dedicated stations, less literature on gauge network specifically |
| Historical flood frequency (10) | 5 — Hirakud Dam regulation reduced severe floods from ~8/decade to ~3/decade — **fewer positive-class events for ML** | 10 — near-annual flooding; documented flood years 2018, 2019, 2020, 2022 in the same sub-basin with consistent methodology | 6 — 2018 was an outlier "once in a century" event; fewer recurring smaller events since |
| Rainfall data availability (10) | 8 | 8 | 8 |
| River-level data availability (10) | 8 | 9 — explicit CWC gauge-level flood bulletins exist naming exact affected blocks/districts (Hojai, Nagaon, Morigaon) | 6 |
| Sentinel-1 SAR coverage & published methodology (10) | 6 — less basin-specific published SAR methodology found | **10 — a directly reusable, published methodology**: Otsu-thresholding on Sentinel-1 VV via Google Earth Engine, validated ≥87% accuracy against Sentinel-2, specifically for Assam (2018–2020), plus a dedicated Kopili River Basin flood-hazard-zonation study covering 183 mapped flood events over two decades | 6 |
| DEM availability (5) | 5 (SRTM/Copernicus, global) | 5 (same, global) | 5 |
| WorldPop availability (5) | 5 | 5 | 5 |
| Census availability (5) | 5 | 5 | 5 |
| OSM completeness (5) | 4 — moderate rural mapping density | 4 — moderate | 5 — Kerala generally has denser OSM mapping |
| Historical flood events documented (10) | 7 — Cyclone Phailin 2013 flooding well documented | 9 — multiple recent, well-reported years with NDRF/NRSC situation reports naming exact affected blocks | 7 — 2018 extremely well documented, but a single dominant event |
| Ease of obtaining training data (10) | 6 | **9** — published GEE/Sentinel-1 workflow is directly reusable by the team to generate flood-extent labels without inventing a new remote-sensing pipeline | 6 |
| Ease of demonstrating the system (5) | 4 | 5 — clear narrative: "Kopili sub-basin floods nearly every monsoon, affecting the same blocks" | 4 |
| Availability of official reports for validation (5) | 4 | 5 — NDRF/NRSC situation reports explicitly name affected blocks/districts by date, ideal for validating GIS impact numbers | 4 |
| **TOTAL /100** | **75** | **93** | **74** |

## FINAL DEMO LOCATION: **Nagaon district, Assam — Kopili sub-basin of the Brahmaputra system**
Primary reference gauge stations: **Kampur and Dharamtul** (Kopili river, CWC network). Fallback/cross-check upstream reference: **Neamatighat** gauge on the main Brahmaputra stem if the team wants a second signal.

**Why this wins decisively**: the deciding factor is not any single row — it's that Nagaon/Kopili is the *only* candidate where a **published, reusable, validated remote-sensing labeling methodology already exists for this exact basin** (Sentinel-1 SAR + Otsu thresholding on Google Earth Engine, ≥87% accuracy against optical Sentinel-2, applied specifically to Assam 2018–2020) combined with **near-annual flood recurrence** (more positive-class training events than a dam-regulated basin like the Mahanadi, where Hirakud has deliberately reduced severe-flood frequency to ~3/decade) and **official government situation reports naming exact affected blocks by date** (NDRF/NRSC 2022 report explicitly names Hojai, Nagaon, and Morigaon as affected by the Kampur/Dharamtul gauge readings) — which your GIS impact numbers can be validated against directly. This is the strongest combination of "we can actually build the training set" and "we can actually prove our numbers are right" available to a student team in the available time.

No further alternatives will be discussed. Build for Nagaon/Kopili.

---

# PHASE 3 — DATA ACQUISITION PLAN

| Dataset | Exact Source | URL | Access | Variables | Time Range | Spatial Res. | Download Method | License | Purpose |
|---|---|---|---|---|---|---|---|---|---|
| CWC gauge data (Kopili) | CWC Flood Forecast Portal / India-WRIS | indiawris.gov.in, cwc.gov.in, aff.india-water.gov.in | Public bulletins/portal; bulk history via written/portal request | Water level, discharge, danger/warning level | As far back as portal/bulletins allow (target min. 3–5 monsoon seasons) | Station point | Scrape published bulletins (dated PDFs/portal tables) + manual request for bulk CSV | Government public data | Primary river-level signal, label source |
| IMD rainfall | IMD (mausam.imd.gov.in) / data.gov.in | mausam.imd.gov.in, data.gov.in | Public; some gridded products request-based | Daily/sub-daily rainfall | Match CWC range | District/gridded (~0.25°) | CSV download / API where available | Government public data | Rainfall feature |
| Sentinel-1 SAR (flood extent labels) | Copernicus Open Access Hub / Google Earth Engine | scihub.copernicus.eu, earthengine.google.com | Free registration | VV polarization, GRD product | 2018–2022 (matches published methodology window) | 10m | GEE Python API (`ee` library) — replicate the Otsu-thresholding workflow directly | Copernicus open license | Flood-extent ground truth / label generation |
| Sentinel-2 (cross-check) | Copernicus Open Access Hub / Bhoonidhi | scihub.copernicus.eu, bhoonidhi.nrsc.gov.in | Free registration | Optical bands | Cloud-free scenes near flood dates | 10m | Same as above | Copernicus/ISRO open | Validate SAR-derived flood extent where cloud-free scenes exist |
| DEM | Copernicus DEM or SRTM | dataspace.copernicus.eu, earthexplorer.usgs.gov | Free registration | Elevation | Static | 30m | Bulk GeoTIFF download for district bounding box | Public/open | Terrain/susceptibility feature, GIS overlay |
| WorldPop | WorldPop | worldpop.org | Free | Gridded population count | Latest annual estimate | 100m | Direct GeoTIFF download for India/Assam | CC BY 4.0 | Population-at-risk calculation |
| Census 2011 | data.gov.in / Census of India | data.gov.in, censusindia.gov.in | Free | Village/ward population | 2011 (latest published) | Village/ward | CSV/shapefile download for Nagaon district | Government open data | Cross-check population baseline |
| OSM roads/buildings/facilities | OpenStreetMap via Overpass API | overpass-api.de | Free | Roads, buildings, hospitals, schools, bridges | Current snapshot | Feature-level | Overpass API query bounded to Nagaon district | ODbL | Infrastructure exposure layer |
| Historical flood situation reports | NDRF/NRSC, CWC daily advisories | ndrf.nrsc.gov.in, cwc.gov.in | Free (PDF) | Affected blocks/villages, dates, water levels | 2018–2022 | Block-level text reports | Manual PDF download, extract structured facts | Government public data | Label validation, demo narrative ground truth |
| District administrative boundaries | Bhuvan / Survey of India-derived open boundary sets | bhuvan.nrsc.gov.in | Free registration | Admin boundaries (district/block/village) | Static | Vector | Shapefile/GeoJSON download | ISRO open | Base admin layer for GIS |

### Datasets we do NOT need for MVP
- Soil moisture (SMAP) — nice-to-have feature, not required for a defensible v1 model; adds an extra data-integration dependency for marginal gain at this scale. **FUTURE.**
- GHSL — redundant with WorldPop + Census for a single-district scope. **SKIP.**
- Landsat imagery — Sentinel-1/2 already covers our labeling need at better temporal frequency. **SKIP.**
- EM-DAT international disaster database — useful for macro context in the PPT, not needed for the training pipeline. **OPTIONAL, PPT-only.**
- IoT/live sensor feeds — no real sensor network exists to integrate for MVP. **FUTURE.**

---

# PHASE 4 — DOWNLOAD THESE FIRST (Minimum Viable Dataset)

1. **CWC Kampur + Dharamtul gauge readings** — as many historical daily/sub-daily water-level readings as can be scraped/requested, minimum 3 monsoon seasons (2018, 2019, 2020 recommended — matches the published SAR methodology window).
2. **IMD district rainfall for Nagaon**, same date range.
3. **Sentinel-1 SAR scenes for the Kopili/Nagaon bounding box**, monsoon months (Jun–Sep) for 2018–2020, pulled via Google Earth Engine.
4. **Copernicus DEM (30m) for Nagaon district bounding box.**
5. **WorldPop 2020 population grid for Assam, clipped to Nagaon district.**
6. **OSM extract (Overpass API) for Nagaon district**: roads, buildings, hospitals, schools.

**If we obtain only these six datasets, we can build the complete MVP**: (1)+(2) train the risk model and provide the live-input feed; (3) generates the flood-extent labels needed to define the ML target and validates GIS output; (4)+(5)+(6) drive the entire GIS impact-assessment and relief-estimation pipeline. Census, historical situation reports, and Sentinel-2 cross-checks are valuable validation/PPT-evidence add-ons, not blockers to starting development.

---

# PHASE 5 — ML DATASET DEFINITION

### One row =
One **(gauge_station, timestamp)** observation, at a fixed cadence (recommend daily, upsampled to sub-daily only if the scraped CWC data actually supports it — do not fabricate sub-daily granularity you don't have).

### Features =
```
station_id
timestamp
rainfall_1d           # rainfall on the day
rainfall_3d_sum        # rolling 3-day cumulative rainfall
rainfall_7d_sum        # rolling 7-day cumulative rainfall
river_level             # current gauge reading
river_level_change_1d   # level minus previous day's level
river_level_change_3d
upstream_level          # Neamatighat or nearest upstream gauge, if available — OPEN DECISION, see below
day_of_year             # captures monsoon seasonality
distance_to_danger_level  # danger_level - current river_level
```

### Target =
Binary classification: **will river level at this station exceed the CWC-defined danger level within the next 24 hours?** (secondary regression target: predicted level itself, for the "expected exceedance magnitude" display — optional stretch goal, not MVP-blocking.)

### Prediction horizon =
**24 hours** for MVP (the masterplan's 6-hour horizon is a stretch goal only if sub-daily data is actually available at sufficient quality — see OPEN DECISION below).

### Label generation =
```
target[station, t] = 1 if max(river_level[station, t+1 .. t+24h]) >= danger_level[station]
                      else 0
```
Conceptually in pandas:
```python
df['future_max_level'] = df.groupby('station_id')['river_level']\
    .transform(lambda s: s.shift(-1).rolling(window=horizon_steps, min_periods=1).max())
df['target'] = (df['future_max_level'] >= df['danger_level']).astype(int)
```
Rows where the future window extends beyond available data are dropped (cannot generate a valid label), not filled with a guess.

### Positive class =
Days where the station's water level crossed the official CWC danger level within the next 24 hours.

### Negative class =
All other days.

### Temporal alignment (rainfall ↔ river level ↔ flood extent)
- Rainfall and river-level series are joined on `date` per station/catchment.
- Sentinel-1-derived flood-extent labels (Phase 3) are used **only as an independent validation set** for the GIS impact-assessment output — not as the primary ML target, because satellite revisit (5–12 days) is too sparse to serve as a daily training label. The daily binary target above (from gauge danger-level crossing) is the actual ML target; satellite imagery cross-checks the *spatial extent* claim on the specific dates imagery exists.

### OPEN DECISION #1: sub-daily granularity and upstream-gauge feature
**Question**: Is CWC bulletin data actually available at sub-daily resolution for Kampur/Dharamtul, and is a Neamatighat upstream reading available for the same dates?
**Minimum experiment to close it**: Day 1 data-scraping spike (2–3 hours) — pull whatever CWC actually publishes for these two stations for one recent flood month and inspect actual cadence/completeness. If only daily granularity exists, freeze the horizon at 24h (already the MVP default above) and drop upstream_level from the feature set if unavailable, rather than blocking on it.

---

# PHASE 6 — LABEL GENERATION PROCESS (detail)

1. Load raw CWC gauge CSV per station: columns `[station_id, date, water_level_m]`.
2. Load official `danger_level` and `warning_level` for each station (published in CWC bulletins/handbooks — a static lookup table, not something the model predicts).
3. Sort by `station_id, date`. Verify monotonic dates, no duplicate timestamps.
4. Compute `future_max_level` as the maximum level over the next N days (N = 1 for the 24h target, using next calendar day's readings — if only daily data exists, "24h horizon" effectively means "tomorrow's reading").
5. Apply the target rule (Phase 5) per row.
6. Drop the final N rows per station (no valid future window) — do **not** label them 0 by default, that would silently inject wrong labels near the end of the series.
7. Sanity check: verify positive-class rate is nontrivial (if it's under ~2%, consider a coarser horizon or accept the imbalance and use class weighting explicitly — do not manufacture positives).
8. Cross-check a sample of labeled positive days against the NDRF/NRSC situation reports (Phase 3) and Sentinel-1 flood-extent maps where available, as a manual spot-validation step — this becomes defensible evidence for your "how did you validate labels" judge answer.

---

# PHASE 7 — ML EXPERIMENT DEFINITION

### Experiment 1 — Baseline
Logistic Regression on `[rainfall_3d_sum, river_level, distance_to_danger_level]` only. Purpose: prove any more complex model actually adds value.

### Experiment 2 — Random Forest
Full feature set (Phase 5), default-ish hyperparameters, purpose: sanity-check tree-based approach before tuning gradient boosting.

### Experiment 3 — XGBoost (primary)
Full feature set, tuned via time-series cross-validation.

### Split (frozen — chronological, event-aware)
- **Train**: 2018–2019 monsoon seasons (plus surrounding months for negative-class density).
- **Validation**: 2020 monsoon season (used for hyperparameter tuning + threshold selection).
- **Test**: held out — if a 2021 or 2022 monsoon season's data can be obtained, use it as the true test set; if not obtainable, reserve the **last 20% of the chronological series** as test and clearly label this as a weaker validation setup in your documentation (do not silently use a random split to inflate metrics).
- **Never** randomly shuffle rows across the split — this leaks future information into training.

### Hyperparameters (XGBoost starting point — tune from here, don't hand-pick a config with no justification)
```
max_depth: 4-6
n_estimators: 200-500 (with early stopping on validation PR-AUC)
learning_rate: 0.05-0.1
scale_pos_weight: (negative_count / positive_count) — set explicitly given known class imbalance
eval_metric: aucpr
```

### Metrics — minimum acceptable evaluation report
```
PR-AUC
Recall @ fixed false-alarm rate (report at 10% and 20% FAR)
Precision @ same operating points
F1
Brier Score (post-calibration)
False Alarm Rate at chosen operating threshold
Missed Event Rate at chosen operating threshold
Lead time distribution (median + min, across correctly-flagged events)
```
### Calibration
Apply Platt scaling (logistic calibration) or isotonic regression on the validation set predictions before reporting confidence scores in the demo UI — an uncalibrated raw XGBoost score should never be shown to judges labeled "confidence: X%."

### Threshold selection
Choose the operating threshold that maximizes recall subject to false-alarm rate ≤ 20% on the validation set; document this choice explicitly rather than picking 0.5 by default (0.5 is meaningless on an imbalanced target).

---

# PHASE 8 — GIS PIPELINE IMPLEMENTATION

1. **Load**: Nagaon district boundary (Bhuvan/admin shapefile), DEM GeoTIFF, WorldPop GeoTIFF, OSM extract (GeoJSON from Overpass), Sentinel-1-derived flood-extent raster/vector (for validation only).
2. **CRS**: standardize everything to **EPSG:32646** (UTM Zone 46N, correct for Assam) for all area/distance calculations; store in PostGIS as **EPSG:4326** (WGS84) for interoperability, reproject on query as needed. Never mix CRSs in a single overlay operation.
3. **Convert/normalize**: reproject all vector layers to EPSG:32646 for analysis; keep DEM/population rasters in their native CRS and reproject via `rasterio.warp` only when needed for a specific overlay.
4. **PostGIS layers** (vector, persistent): district/block boundaries, roads, buildings, hospitals/schools/shelters, computed hazard-zone polygons, computed affected-zone results.
5. **Remain as raster files** (not loaded into PostGIS row-by-row): DEM, population grid, Sentinel imagery — queried via `rasterio`/`rasterstats` for zonal statistics, results (aggregated numbers) then written into PostGIS/Postgres tables.
6. **Hazard zone generation**: (a) take the ML model's per-station risk score, (b) combine with a static DEM-derived susceptibility index (e.g., Height Above Nearest Drainage proxy, or simply "cells below X meters relative elevation within Y km of the river centerline" as a pragmatic MVP simplification), (c) produce a hazard polygon per risk level (LOW/MED/HIGH) via thresholding + `rasterio.features.shapes` to vectorize.
7. **Population-at-risk**: `rasterstats.zonal_stats(hazard_polygon, worldpop_raster, stats='sum')`.
8. **Infrastructure exposure**: PostGIS `ST_Intersects(hazard_polygon, facility_point)` count, plus a buffered "cut off but not flooded" category via `ST_DWithin`.
9. **Road analysis**: PostGIS `ST_Intersects` for affected length (`ST_Length` of intersected segments); accessibility via a simple graph shortest-path (`networkx` on OSM road graph, or `pgRouting` if PostGIS extension available) from nearest unaffected node.
10. **Priority score**: computed in Python/SQL per the frozen formula (masterplan Part 9.2), written to `affected_zones.priority_score`.

### Database geometry types
- `district_boundaries.geom`: `POLYGON, SRID 4326`
- `hazard_zones.geom`: `POLYGON, SRID 4326` (generated per prediction run)
- `roads.geom`: `LINESTRING/MULTILINESTRING, SRID 4326`
- `infrastructure.geom`: `POINT, SRID 4326`
- `affected_zones.geom`: `POLYGON, SRID 4326`

---

# PHASE 9 — RELIEF ENGINE (frozen formula)

### Inputs
```
affected_population   # from GIS (Phase 8)
severity               # LOW=0.3 / MEDIUM=0.6 / HIGH=1.0, from risk_score bucketing
duration_days          # policy default = 3
water_norm_l_per_person_per_day   = 15      # Sphere standard
food_kit_per_person                = 1       # 1 food kit assumed to cover ~2100 kcal/day — ASSUMPTION, tune with real ration-kit spec if available
medicine_kit_per_persons           = 1 per 5 persons   # ASSUMPTION — replace with actual state health-dept norm if obtained
shelter_kit_per_persons            = 1 per 5 persons   # ASSUMPTION — household-size proxy
buffer_factor                      = 1.15
```

### Output JSON (frozen contract)
```json
{
  "zone_id": "NAGAON-KOPILI-Z07",
  "population_at_risk": 12500,
  "severity": "HIGH",
  "duration_days": 3,
  "water_litres": 646875,
  "food_kits": 14375,
  "medical_kits": 2875,
  "shelter_kits": 2875,
  "assumptions": {
    "water_norm_l_per_person_per_day": "15L — Sphere Handbook minimum standard (sourced)",
    "food_kit_ratio": "1 kit/person/day ≈ 2100kcal — ASSUMPTION, not government-verified",
    "medical_kit_ratio": "1 kit per 5 persons — ASSUMPTION",
    "shelter_kit_ratio": "1 kit per 5 persons (household proxy) — ASSUMPTION",
    "buffer_factor": "1.15 — ASSUMPTION, logistics contingency"
  }
}
```
Formula: `quantity = affected_population × severity × duration_days × per_person_norm × buffer_factor` for water; food/medical/shelter use the ratio-based ASSUMPTION fields above rather than the raw per-person norm, since credible per-kit norms weren't found in public sources for this pass — **label these explicitly as assumptions in the PPT and be ready to swap in a real government norm if your team finds one before the demo.**

---

# PHASE 10 — ALLOCATION ENGINE (frozen)

### Inputs
- `warehouses[w] = {location, stock[resource_type]}`
- `zones[z] = {location, demand[resource_type], priority_score}`
- `travel_time[w][z]` (precomputed via road-network shortest path or straight-line distance as MVP fallback)

### Variables
`shipped[w][z]` ≥ 0 — quantity of a given resource type shipped from warehouse w to zone z.

### Objective (minimize)
```
Σ_z (unmet_demand[z] × priority_score[z] × PENALTY_WEIGHT)
+ Σ_(w,z) (shipped[w,z] × travel_time[w,z])
```

### Constraints
```
Σ_z shipped[w,z] ≤ stock[w]         for every warehouse w
Σ_w shipped[w,z] ≤ demand[z]        for every zone z
shipped[w,z] ≥ 0
```

### Output
```json
[
  {"warehouse_id": "WH-A", "zone_id": "NAGAON-KOPILI-Z07", "resource_type": "water", "quantity": 400000, "recommended_route": "..."},
  {"warehouse_id": "WH-B", "zone_id": "NAGAON-KOPILI-Z07", "resource_type": "water", "quantity": 246875, "recommended_route": "..."}
]
```

### Worked example
```
Warehouses: WH-A (stock: 500,000L water), WH-B (stock: 300,000L water)
Zones: Z1 (demand 400,000L, priority 90), Z2 (demand 200,000L, priority 60), Z3 (demand 200,000L, priority 40)

Solver output (illustrative):
WH-A → Z1: 400,000L   (highest priority fully served first, nearest warehouse)
WH-A → Z2: 100,000L   (remaining WH-A stock)
WH-B → Z2: 100,000L   (fills remaining Z2 demand)
WH-B → Z3: 200,000L   (WH-B remaining stock exactly covers Z3)
```

### OR-Tools implementation
Use `ortools.linear_solver.pywraplp` with the `GLOP` or `CBC` backend (CBC if you want strict integer unit counts for kits, GLOP is fine for continuous quantities like litres). This problem size (a handful of warehouses × a handful of zones) solves in milliseconds — no performance concern for MVP.

---

# PHASE 11 — BLOCKCHAIN: FREEZE THE IMPLEMENTATION

### OPEN DECISION #2 (must be closed on Day 1–2): Fabric vs. testnet
**Minimum experiment**: allocate a fixed 4-hour timebox on Day 1 for whoever owns blockchain to attempt a minimal `hyperledger/fabric-samples` "test-network" bring-up (2 orgs, 1 channel) using the standard Fabric samples repo. **If it is running and a chaincode can be installed within that 4-hour box, commit to Fabric for the rest of the build.** If not, fall back immediately to Solidity + Hardhat local network — do not keep attempting Fabric past the timebox, and state the substitution explicitly in your docs/demo per the masterplan's honesty requirement.

### Organizations (MVP, either platform)
- **District Administration** (approves requests, allocates resources)
- **NGO** (dispatches, confirms delivery)
- **Warehouse** (confirms stock release)

### Fabric network (if chosen)
- 3 peer organizations (District Admin, NGO, Warehouse), 1 peer each for MVP (production would use 2+ peers/org for fault tolerance — not needed for a demo).
- 1 ordering service node (Raft — the standard modern Fabric ordering service; single-node Raft is acceptable for MVP, it doesn't need multi-node BFT for a hackathon demo).
- 1 channel: `relief-channel`, all 3 orgs joined (single-channel model is sufficient for MVP — do not build per-organization private channels for MVP, that's a production hardening step).
- Identities/MSPs: use Fabric CA to issue one identity per organization's admin user for MVP (do not attempt per-field-officer individual identities within the hackathon timebox — that's a real production requirement but out of MVP scope).

### Chaincode (frozen function list)

| Function | Input | Caller | Validation | State Change | Event |
|---|---|---|---|---|---|
| `createReliefRequest` | zoneId, resourceType, quantity, requestingOrgId | District Admin or NGO | requestingOrgId is a known MSP | new asset, status=REQUESTED | `RequestCreated` |
| `approveRequest` | requestId, approverId | District Admin only | caller MSP == DistrictAdmin, current status==REQUESTED | status→APPROVED | `RequestApproved` |
| `allocateResource` | requestId, warehouseId, quantity | District Admin | status==APPROVED, quantity ≤ declared warehouse stock (checked off-chain, referenced on-chain) | status→ALLOCATED, new allocation asset created | `ResourceAllocated` |
| `dispatchResource` | allocationId, vehicleId | Warehouse org | caller MSP == Warehouse, status==ALLOCATED | status→DISPATCHED | `ResourceDispatched` |
| `markInTransit` | allocationId | Warehouse or NGO | status==DISPATCHED | status→IN_TRANSIT | `InTransit` |
| `verifyDelivery` | allocationId, evidenceHash | NGO org (field role) | status==IN_TRANSIT or DELIVERED, evidenceHash non-empty | status→VERIFIED | `DeliveryVerified` |
| `flagDiscrepancy` | allocationId, reporterId, reason | Any org member | status in {DISPATCHED, IN_TRANSIT, DELIVERED, VERIFIED} | status→DISPUTED | `DiscrepancyFlagged` |
| `resolveDispute` | allocationId, resolverId, outcome | District Admin only | caller MSP == DistrictAdmin, status==DISPUTED | status→RESOLVED (with outcome note) | `DisputeResolved` |

---

# PHASE 12 — BLOCKCHAIN DATA MODEL (frozen asset structure)

```json
{
  "allocationId": "ALLOC-2026-0001",
  "disasterId": "NAGAON-FLOOD-2026-08",
  "sourceOrg": "WH-A",
  "destinationOrg": "NGO-XYZ",
  "resourceType": "water",
  "quantity": 400000,
  "status": "DISPATCHED",
  "createdAt": "2026-08-27T10:15:00Z",
  "updatedAt": "2026-08-27T11:02:00Z",
  "zoneId": "NAGAON-KOPILI-Z07",
  "proofHash": "sha256:6f1ed002ab5595859014ebf0951522d9..."
}
```

### Field justification
- `allocationId` — primary key, links to off-chain Postgres record.
- `disasterId` — groups all transactions under one event for audit queries.
- `sourceOrg`/`destinationOrg` — MSP identifiers, establishes who-sent-to-whom without needing PII.
- `resourceType`/`quantity` — the actual movement being tracked.
- `status` — drives the state machine (Phase 11).
- `createdAt`/`updatedAt` — timestamps, immutable once written.
- `zoneId` — links to GIS zone, not raw GPS coordinates of any individual.
- `proofHash` — SHA-256 hash of the off-chain evidence bundle (photo + GPS log + OTP confirmation JSON) — the only pointer to delivery evidence; the evidence itself never touches the chain.

### ON-CHAIN
`allocationId, disasterId, sourceOrg, destinationOrg, resourceType, quantity, status, timestamps, zoneId, proofHash`

### OFF-CHAIN (PostgreSQL + object storage, referenced by hash)
Delivery photos, raw GPS traces, OTP logs, recipient names/phone numbers (PII), full relief-request text, raw sensor/rainfall data, raw model internals.

**No PII, no satellite imagery, no large files, ever go on-chain.**

---

# PHASE 13 — DELIVERY VERIFICATION (MVP-realistic)

### What we actually implement for SIH
**GPS (simulated) + photo hash (real hashing of an actual uploaded photo) + OTP (simulated SMS, real OTP-matching logic)** — dual confirmation (field officer digital signature + recipient OTP) is the target; if time-constrained, single-factor (photo + officer signature) with the rest documented as FUTURE is an acceptable fallback — **do not fake a QR-scanning hardware flow you have no device for.**

| Step | Field user | Action | Evidence | Backend validation | Blockchain tx | Status transition |
|---|---|---|---|---|---|---|
| 1 | NGO field officer | Opens delivery task, takes geotagged photo | Photo file + EXIF GPS + timestamp | Backend checks GPS is within expected zone polygon (PostGIS `ST_Contains`) | none yet | DISPATCHED→IN_TRANSIT (on dispatch confirm) |
| 2 | NGO field officer | Enters recipient confirmation (OTP sent to registered contact, or community-rep sign-off) | OTP match or signature capture | Backend validates OTP against issued code (simulated SMS provider for demo) | none yet | IN_TRANSIT→DELIVERED |
| 3 | Backend | Bundles photo+GPS+OTP-log into an evidence object, computes SHA-256 | evidence bundle hash | Bundle stored in object storage, hash computed | `verifyDelivery(allocationId, evidenceHash)` called | DELIVERED→VERIFIED |
| Failure path | Auditor or any org member | Notices mismatch (e.g., GPS outside zone, no OTP match) | — | — | `flagDiscrepancy(...)` called | VERIFIED (or DELIVERED)→DISPUTED→INVESTIGATED→RESOLVED |

```
DISPATCHED → IN_TRANSIT → DELIVERED → VERIFICATION → VERIFIED
                                            ↓ (mismatch)
                                         FAILED → DISPUTED → INVESTIGATED → RESOLVED
```

---

# PHASE 14 — DATABASE IMPLEMENTATION (DDL-level)

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  org_type TEXT NOT NULL CHECK (org_type IN ('gov','ngo','warehouse')),
  verified BOOLEAN DEFAULT false
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  org_id UUID REFERENCES organizations(id),
  contact TEXT,
  password_hash TEXT NOT NULL
);

CREATE TABLE disasters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hazard_type TEXT NOT NULL DEFAULT 'flood',
  district TEXT NOT NULL DEFAULT 'Nagaon',
  start_time TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE gauge_stations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,          -- 'Kampur', 'Dharamtul'
  geom GEOMETRY(POINT, 4326) NOT NULL,
  danger_level_m NUMERIC,
  warning_level_m NUMERIC
);

CREATE TABLE sensor_readings (
  id BIGSERIAL PRIMARY KEY,
  station_id UUID REFERENCES gauge_stations(id),
  timestamp TIMESTAMPTZ NOT NULL,
  water_level_m NUMERIC,
  rainfall_mm NUMERIC,
  source TEXT
);
CREATE INDEX idx_sensor_readings_station_time ON sensor_readings(station_id, timestamp);

CREATE TABLE predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  disaster_id UUID REFERENCES disasters(id),
  station_id UUID REFERENCES gauge_stations(id),
  timestamp TIMESTAMPTZ NOT NULL,
  risk_score NUMERIC NOT NULL,
  severity TEXT NOT NULL,
  confidence NUMERIC NOT NULL,
  model_version TEXT NOT NULL
);

CREATE TABLE affected_zones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  disaster_id UUID REFERENCES disasters(id),
  geom GEOMETRY(POLYGON, 4326) NOT NULL,
  population_at_risk INT,
  infra_at_risk_json JSONB,
  priority_score NUMERIC
);
CREATE INDEX idx_affected_zones_geom ON affected_zones USING GIST(geom);

CREATE TABLE infrastructure (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type TEXT NOT NULL,           -- hospital/school/shelter/road_node
  geom GEOMETRY(POINT, 4326) NOT NULL,
  name TEXT,
  source TEXT
);
CREATE INDEX idx_infrastructure_geom ON infrastructure USING GIST(geom);

CREATE TABLE roads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  geom GEOMETRY(MULTILINESTRING, 4326) NOT NULL,
  name TEXT,
  source TEXT
);
CREATE INDEX idx_roads_geom ON roads USING GIST(geom);

CREATE TABLE population_grid (
  id BIGSERIAL PRIMARY KEY,
  geom GEOMETRY(POLYGON, 4326) NOT NULL,
  population NUMERIC,
  source TEXT,
  year INT
);
CREATE INDEX idx_population_grid_geom ON population_grid USING GIST(geom);

CREATE TABLE warehouses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID REFERENCES organizations(id),
  geom GEOMETRY(POINT, 4326) NOT NULL,
  capacity_json JSONB
);

CREATE TABLE resources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  warehouse_id UUID REFERENCES warehouses(id),
  resource_type TEXT NOT NULL,
  quantity NUMERIC NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE relief_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  zone_id UUID REFERENCES affected_zones(id),
  resource_type TEXT NOT NULL,
  quantity_requested NUMERIC NOT NULL,
  status TEXT NOT NULL DEFAULT 'REQUESTED',
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE allocations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id UUID REFERENCES relief_requests(id),
  warehouse_id UUID REFERENCES warehouses(id),
  quantity_allocated NUMERIC NOT NULL,
  status TEXT NOT NULL DEFAULT 'ALLOCATED',
  chain_tx_hash TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE shipments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  allocation_id UUID REFERENCES allocations(id),
  vehicle_id TEXT,
  dispatch_time TIMESTAMPTZ,
  route_geom GEOMETRY(LINESTRING, 4326)
);

CREATE TABLE deliveries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  shipment_id UUID REFERENCES shipments(id),
  delivered_at TIMESTAMPTZ,
  evidence_hash TEXT,
  verified BOOLEAN DEFAULT false
);

CREATE TABLE verification_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  delivery_id UUID REFERENCES deliveries(id),
  method TEXT NOT NULL,        -- 'photo+gps' / 'otp' / 'signature'
  evidence_ref TEXT,           -- object storage path
  verified_by UUID REFERENCES users(id),
  verified_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE blockchain_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  related_entity_type TEXT NOT NULL,   -- 'allocation'
  related_entity_id UUID NOT NULL,
  tx_hash TEXT NOT NULL,
  block_ref TEXT,
  timestamp TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  actor_id UUID REFERENCES users(id),
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id UUID,
  timestamp TIMESTAMPTZ DEFAULT now(),
  details_json JSONB
);
```

No tables beyond this list for MVP — this is intentionally the complete and final schema.

---

# PHASE 15 — API CONTRACT (frozen)

```
POST   /auth/login                        Body: {email, password} → {token, role, org_id}          401 on failure

POST   /disasters                         Auth: gov               Body: {hazard_type, district, start_time} → {id}
GET    /disasters/{id}                    Auth: any authenticated → {disaster object}

GET    /predictions/{disasterId}          Auth: any authenticated → [{station_id, risk_score, severity, confidence, timestamp}]
GET    /risk-zones?disasterId=            Auth: any authenticated → GeoJSON FeatureCollection

GET    /impact-assessment/{zoneId}        Auth: any authenticated → {population_at_risk, infra_at_risk, priority_score}

POST   /relief-request                    Auth: gov or ngo        Body: {zone_id, resource_type, quantity} → {id, status}   400 if zone unknown
POST   /allocation                        Auth: gov                Body: {request_id} → triggers OR-Tools, returns [{warehouse_id, quantity, route}]   409 if already allocated
POST   /allocation/{id}/approve           Auth: gov                → {status: APPROVED} — human-in-the-loop gate, writes to chain
POST   /dispatch                          Auth: warehouse          Body: {allocation_id, vehicle_id} → {status: DISPATCHED}
POST   /delivery/verify                   Auth: ngo (field role)   Body: {allocation_id, photo, gps, otp} → {status: VERIFIED|FAILED}   422 if evidence incomplete

GET    /blockchain/transaction/{id}       Auth: any authenticated → {tx_hash, status, timestamps}
POST   /dispute                           Auth: any authenticated  Body: {allocation_id, reason} → {status: DISPUTED}

GET    /dashboard/gov                     Auth: gov                → aggregated view payload
GET    /dashboard/ngo                     Auth: ngo                → org-scoped view payload
GET    /dashboard/public                  Auth: none (public)      → aggregate-only, no PII
```
**AuthN**: JWT bearer token, issued at login, 8-hour expiry for MVP. **AuthZ**: role checked server-side on every endpoint per the "Auth:" column above; a request from a role not listed returns 403.

---

# PHASE 16 — REPOSITORY STRUCTURE (final)

```
SETU/
├── docs/                # PRD, this frozen spec, model card, smart contract spec
├── data/
│   ├── raw/              # gitignored — CWC/IMD/Sentinel/DEM/WorldPop/OSM downloads
│   └── processed/        # cleaned/joined tables, feature-engineered training set
├── ml/
│   ├── notebooks/         # exploration
│   ├── pipeline/          # feature engineering, label generation, training scripts
│   └── models/            # saved model artifacts
├── gis/
│   ├── overlay/            # spatial overlay computation
│   └── zonal_stats/        # rasterstats scripts
├── relief/                # relief estimation formula module
├── optimization/           # OR-Tools allocation engine
├── blockchain/
│   ├── chaincode/           # Fabric chaincode (Go/JS) OR contracts/ (Solidity), depending on Phase 11 decision
│   └── network/              # network bring-up scripts/config
├── backend/                # FastAPI app, one router file per API group (Phase 15)
├── frontend/                # React app, gov/ngo/public dashboard routes
├── scripts/                 # data download/scraping scripts, demo-scenario replay script
├── tests/                   # unit/integration/ML/GIS/contract tests
├── docker/                  # docker-compose.yml, per-service Dockerfiles
└── README.md
```

---

# PHASE 17 — DOCKER / LOCAL DEVELOPMENT

**Minimum development environment (frozen)**:

```yaml
# docker-compose.yml services
postgres:      # postgis/postgis:16-3.4 image, exposes 5432
backend:       # FastAPI app, exposes 8000, depends_on postgres
frontend:      # React dev server, exposes 3000
```

**ML and GIS run as scripts/notebooks locally against the same Postgres**, not as always-on containers for MVP — this avoids container overhead for compute-heavy one-off training/overlay jobs that don't need to be "services" during the hackathon.

**Blockchain runs separately**: if Fabric, use the standard `fabric-samples/test-network` scripts (`network.sh up`, `network.sh createChannel`) outside docker-compose (Fabric's own tooling manages its containers); if Solidity/Hardhat, run `npx hardhat node` locally — also outside the main compose file, since it's a distinct network with its own lifecycle.

**Object storage**: for MVP, store evidence files (photos) directly on local disk under a `backend/storage/` volume mount — do not stand up MinIO/S3 for a hackathon demo unless the team already has it wired up; this is a deliberate simplification.

```bash
git clone <repo>
cd SETU
docker compose up -d postgres backend frontend
# separately, per Phase 11 decision:
cd blockchain/network && ./network.sh up   # Fabric
# OR
cd blockchain && npx hardhat node          # Solidity fallback
```

---

# PHASE 18 — TEAM TASK BOARD

### Person 1 — AI/ML
| Task ID | Task | Dependency | Est. time | Deliverable | DoD |
|---|---|---|---|---|---|
| ML-1 | Scrape/assemble CWC+IMD historical data for Kampur/Dharamtul | Data-1 (raw files) | 6h | raw CSVs in `data/raw/` | Files present, spot-checked for date coverage |
| ML-2 | Build label generation pipeline (Phase 6) | ML-1 | 4h | `ml/pipeline/labels.py` | Positive-class rate sanity-checked, cross-validated against ≥3 known flood dates |
| ML-3 | Feature engineering (Phase 5) | ML-2 | 4h | `ml/pipeline/features.py` | Feature table matches frozen schema |
| ML-4 | Train Experiment 1–3 (Phase 7) | ML-3 | 8h | `ml/models/*.pkl` + eval report | Metrics table (Phase 7) fully populated |
| ML-5 | Calibration + threshold selection | ML-4 | 3h | Calibrated model | Brier score reported, threshold documented with justification |
| ML-6 | Inference API wrapper | ML-5, BE-1 | 3h | `/predictions` endpoint logic | Returns risk_score/severity/confidence per frozen contract |

### Person 2 — Data Engineering
| Task ID | Task | Dependency | Est. time | Deliverable | DoD |
|---|---|---|---|---|---|
| Data-1 | Set up PostGIS, run DDL (Phase 14) | — | 2h | Running DB with all tables | `\dt` shows all frozen tables |
| Data-2 | Download DEM/WorldPop/OSM for Nagaon (Phase 4) | — | 4h | Files in `data/raw/` | Bounding box confirmed correct via QGIS visual check |
| Data-3 | Load static layers into PostGIS (roads, infra, population_grid, gauge_stations) | Data-1, Data-2 | 5h | Populated tables | Row counts sane, spatial index built, one test query returns expected result |
| Data-4 | Sentinel-1 GEE flood-extent extraction (Phase 3) | — | 6h | Flood-extent vectors for validation | Extent overlaps at least one known 2020 flood report location |

### Person 3 — GIS
| Task ID | Task | Dependency | Est. time | Deliverable | DoD |
|---|---|---|---|---|---|
| GIS-1 | Hazard-zone generation from risk score + DEM susceptibility (Phase 8.6) | ML-6, Data-3 | 6h | `gis/overlay/hazard_zone.py` | Produces a valid polygon for a test prediction |
| GIS-2 | Population-at-risk + infra exposure calc | GIS-1 | 4h | `gis/zonal_stats/impact.py` | Matches manual spot-check on one test zone |
| GIS-3 | Road accessibility + priority score | GIS-2 | 4h | Priority score written to `affected_zones` | Score changes sensibly when test inputs change |
| GIS-4 | `/impact-assessment` endpoint logic | GIS-3, BE-1 | 2h | Endpoint returns frozen JSON contract | Matches Phase 15 contract exactly |

### Person 4 — Blockchain
| Task ID | Task | Dependency | Est. time | Deliverable | DoD |
|---|---|---|---|---|---|
| BC-1 | Fabric-vs-testnet decision spike (OPEN DECISION #2) | — | 4h (hard timebox) | Decision documented | Either Fabric test-network running, or explicit fallback decision logged |
| BC-2 | Chaincode/contract implementation (Phase 11 function table) | BC-1 | 8h | Deployed chaincode/contract | All 8 functions callable, state machine enforced |
| BC-3 | Backend integration (submit tx on allocation approval, verify, dispute) | BC-2, BE-2 | 5h | `blockchain/` client module used by backend | End-to-end: API call → chain tx → tx hash stored in `blockchain_transactions` |

### Person 5 — Backend
| Task ID | Task | Dependency | Est. time | Deliverable | DoD |
|---|---|---|---|---|---|
| BE-1 | Scaffold FastAPI app, auth, all endpoint stubs (Phase 15) | Data-1 | 5h | Running API with stub responses | Every endpoint in Phase 15 returns correctly-shaped mock data |
| BE-2 | Wire real logic into endpoints as ML/GIS/relief/optimization/blockchain modules complete | ML-6, GIS-4, RA-2, BC-3 | 8h (spread across build) | Fully wired API | End-to-end demo scenario succeeds via API calls alone (no UI needed) |
| BE-3 | RBAC enforcement + audit logging | BE-1 | 3h | Middleware | Unauthorized role gets 403 on every protected endpoint (test each) |

### Person 6 — Frontend/DevOps/Product
| Task ID | Task | Dependency | Est. time | Deliverable | DoD |
|---|---|---|---|---|---|
| FE-1 | Gov dashboard: map, risk zones, approve button | BE-1 (stub OK to start) | 8h | React view | Officer can view risk zones and click Approve, hitting real API by Day 3 |
| FE-2 | NGO dashboard: assigned requests, dispatch/verify UI | BE-1 | 6h | React view | NGO user sees only their org's data (RBAC-scoped) |
| FE-3 | Public dashboard: alerts + aggregate stats | BE-1 | 3h | React view | No PII visible, aggregate numbers only |
| FE-4 | docker-compose + deployment | BE-1 | 3h | Working `docker compose up` | Fresh clone + compose up works on a teammate's machine |
| FE-5 | PPT + demo narration script | (near end) | ongoing | Final PPT, demo script | Matches masterplan slide structure, REAL/SIMULATED labels correct |

---

# PHASE 19 — FIRST 72 HOURS

### Day 1
- Morning: freeze roles (this document, Phase 18), set up repo (Phase 16), `docker compose up` running for everyone.
- Data-1/Data-2 start downloading Phase 4 datasets immediately.
- ML-1 starts CWC/IMD scraping immediately (highest risk item — start first).
- BC-1 runs the Fabric decision spike (hard 4h timebox) — **by end of Day 1, blockchain platform must be decided.**
- BE-1 scaffolds the full API with stub responses so frontend can start immediately without waiting.

### Day 2
- ML-2/ML-3: labels + features built on whatever data was obtained Day 1.
- Data-3/Data-4: static layers loaded into PostGIS, Sentinel extraction running.
- GIS-1 starts as soon as any prediction (even a stub score) is available.
- BC-2: chaincode/contract implementation begins.
- FE-1/FE-2/FE-3: build against BE-1's stub responses.

### Day 3
- ML-4/ML-5: model trained, evaluated, calibrated.
- GIS-2/GIS-3: impact numbers + priority score computed on real data.
- RA (relief/allocation, folded into GIS or Backend owner if no dedicated person): formula + OR-Tools wired.
- BC-3: backend-blockchain integration.
- BE-2: real logic replacing stubs, endpoint by endpoint.

### At the end of 72 hours, we should have:
1. A trained, evaluated XGBoost model with a documented metrics report (Phase 7).
2. A populated PostGIS database with all static layers for Nagaon district.
3. A decided (not still-debated) blockchain platform, with basic chaincode/contract functions deployed and callable.
4. A backend API where at least `/predictions`, `/risk-zones`, and `/impact-assessment` return real (not stubbed) data end-to-end.

**If we don't have these four things, we are behind — stop adding features and consolidate on making these four work before touching anything else (dashboards, delivery verification, dispute flow can slip into the remaining days; these four cannot).**

---

# PHASE 20 — FIRST WORKING VERTICAL SLICE

Build this **before** polishing any individual component:

```
Historical rainfall + river level (real, one station, one date range)
↓
XGBoost (even a rough, uncalibrated first version)
↓
Risk score (single number, single station)
↓
One hardcoded/simplified GIS polygon (doesn't need the full susceptibility model yet — a buffer around the gauge station is an acceptable Day-2 placeholder)
↓
Population estimate (real zonal stat on that placeholder polygon)
↓
Relief estimate (real formula on that real population number)
↓
One allocation (even hardcoded warehouse-to-zone, OR-Tools can come after this slice proves the concept)
↓
One blockchain transaction (real tx on whichever platform was decided)
↓
Dashboard shows this one number end-to-end
```

**Build order justification**: get every layer of the stack touched by real data at least once, end-to-end, as early as possible (target: end of Day 2). This de-risks integration — the single biggest hackathon failure mode is five polished components that were never actually connected together until the final night. Once this slice works, go back and replace each placeholder (hardcoded polygon → real susceptibility model, hardcoded allocation → real OR-Tools call) one at a time, re-testing the full chain after each swap.

---

# PHASE 21 — PPT EVIDENCE REQUIREMENTS

| Claim | Evidence needed | Source | Where in PPT |
|---|---|---|---|
| "Existing systems don't do hyper-local relief orchestration" | Gap table (masterplan Part 3) | CWC/NDMA/Bhuvan official descriptions | Slide 3 |
| "Flood is the right first hazard" | Data-availability comparison (Phase 2 scoring table) | This document | Slide 2/backup slide |
| "Our model adds value over raw CWC forecast" | Baseline (logistic regression) vs. XGBoost metrics comparison | Phase 7 eval report | Slide 5 |
| "Model is well-calibrated, not just accurate-looking" | Reliability diagram / Brier score | Phase 7 output | Slide 5 backup |
| "Population impact numbers are credible" | Cross-check against NDRF/NRSC situation report for a known historical date | Phase 3/6 validation step | Slide 6 |
| "Relief estimation is defensible, not arbitrary" | Sphere Handbook citation for water/food norms, explicit ASSUMPTION labels for the rest | Phase 9 | Slide 7 |
| "Blockchain is actually necessary" | Cross-organization trust argument (masterplan Part 12.2) + platform comparison table | Masterplan | Slide 8 |
| "Delivery verification is real, not hand-waved" | The dual-confirmation flow diagram (Phase 13) | This document | Slide 9 |
| "System is realistically deployable" | Feasibility table (masterplan Part 22), pilot cost estimate | Masterplan | Slide 12 |
| "We know what's real vs. simulated" | REAL/MOCKED/SIMULATED table (masterplan Part 25), populated with actual Day-14 build status | Your actual completed build | Slide 11 |

---

# PHASE 22 — "START HERE TOMORROW MORNING"

### 1. Exact geography
**Nagaon district, Assam — Kopili sub-basin of the Brahmaputra system.** Primary gauge stations: **Kampur, Dharamtul.**

### 2. Exact datasets to download (in priority order)
1. CWC gauge history — Kampur & Dharamtul (scrape/request via cwc.gov.in / indiawris.gov.in)
2. IMD rainfall for Nagaon district (mausam.imd.gov.in / data.gov.in)
3. Sentinel-1 SAR, Jun–Sep 2018–2020, via Google Earth Engine, Nagaon/Kopili bounding box
4. Copernicus DEM 30m, Nagaon district bounding box
5. WorldPop 2020, clipped to Nagaon district
6. OSM extract via Overpass API, Nagaon district (roads, buildings, hospitals, schools)

### 3. Exact software to install
```
Python 3.11+, PostgreSQL 16 + PostGIS 3.4, Docker + docker-compose
Python: pandas, geopandas, rasterio, rasterstats, xgboost, scikit-learn, fastapi, uvicorn, ortools, shapely, earthengine-api
Node.js 20+, React (via Vite), 
Blockchain: hyperledger/fabric-samples (Go + Docker) OR Node.js + Hardhat + Solidity — decided Day 1 per BC-1
QGIS Desktop (for visual validation, not required in the pipeline itself)
```

### 4. Exact GitHub structure
See Phase 16 — create it verbatim, commit an empty README per folder to preserve structure in git.

### 5. Exact documents to create (Day 1, before heavy coding)
- This frozen spec (already done — commit it to `docs/`)
- One-page PRD summary (can extract from masterplan)
- Smart Contract Specification (Phase 11–12, commit to `docs/`)
- Data Source Register (Phase 3, commit to `docs/`)

### 6. Exact first tasks for each team member
See Phase 18, Day-1 rows: ML-1, Data-1+Data-2, BC-1, BE-1 all start in parallel, immediately.

### 7. Exact first ML experiment
Experiment 1 (Logistic Regression baseline) on `[rainfall_3d_sum, river_level, distance_to_danger_level]`, run the moment ML-2/ML-3 produce even a partial labeled dataset — don't wait for the full historical range to be collected before running a first pass.

### 8. Exact first GIS experiment
Load Nagaon district boundary + one gauge station point into PostGIS, draw a simple 5km buffer polygon around Kampur as a placeholder hazard zone, run `zonal_stats` against the WorldPop raster to get a population number — this is the Phase 20 vertical-slice GIS step, do it on Day 1–2 before building the real susceptibility model.

### 9. Exact first blockchain experiment
Run the BC-1 4-hour Fabric spike (`fabric-samples/test-network` up + install a "hello world" chaincode) on Day 1; if it fails within the timebox, immediately switch to `npx hardhat init` + a minimal Solidity contract with just `createReliefRequest` and `approveRequest` to prove the toolchain works end-to-end, then build out the rest of the function list (Phase 11) on whichever platform was chosen.

### 10. Exact first end-to-end demo
The Phase 20 vertical slice: one station's real rainfall/level data → rough risk score → placeholder GIS polygon → real population number → real relief formula output → one hardcoded allocation → one real blockchain transaction → visible on a bare-bones dashboard page (even an unstyled React page listing the JSON is enough for this first pass). Target: working by end of Day 2. Everything after this is refinement, not new capability.

---

**No further scope discussion. Build.**
