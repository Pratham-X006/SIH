# SETU — AI-Powered Disaster Early Warning, Impact Assessment & Transparent Relief Management
## Complete Technical Master Plan & Pitch Foundation — SIH 2026, PS ID: IHSIH027

*Prepared as a build-ready blueprint and judge-defense document. Every claim below is marked as **VALIDATED** (backed by cited public sources), **ASSUMPTION** (a stated, labeled estimate), or **DEMO SIMULATION** (mocked for the hackathon only). Nothing here should be presented to judges as fact unless it carries one of these labels honestly.*

---

## 1. EXECUTIVE SUMMARY

Your original framing — "AI + GIS + Blockchain, four modules, Predict→Assess→Estimate→Allocate→Track→Verify" — is directionally sound but currently reads as a **technology checklist**, not a **decision system**. Judges at SIH grade orchestration and defensibility, not buzzword coverage. The rebuild below keeps your four pillars but does three things differently:

1. **Repositions the product** as a *decision-support and transparency orchestration layer* sitting on top of NDMA/IMD/CWC/NRSC — never a replacement for them. This is not just diplomatic framing; it is the only technically honest position, because India already operates real-time flood forecasting infrastructure a six-person student team cannot and should not try to rebuild: CWC's National Flood Forecasting Network issues roughly 10,000 forecasts a year from 332 stations [CWC], and CWC + C-DAC + NRSC just launched C-FLOOD, a 2-D hydrodynamic web system that sounds village-level alarms up to two days ahead for the Mahanadi, Godavari and Tapi basins under the National Supercomputing Mission [Deccan Herald/CWC]; ISRO/NRSC's Bhuvan-Disaster / NDEM geoportal separately provides satellite-based flood, cyclone and landslide mapping [NRSC/Bhuvan].
2. **Narrows the AI task** from "predict disasters" (vague, unfalsifiable) to a specific, gradable target: short-horizon flood-risk probability at a defined spatial unit, explicitly downstream of official rainfall/river data rather than competing with it.
3. **Replaces "blockchain because the PS says blockchain" with a scoped, justified permissioned-ledger design** that records only the relief supply-chain transaction trail (allocation → dispatch → delivery → verification), not sensor data, not PII, not raw predictions — because that is the only part of this problem that is actually a multi-party trust problem.

**Recommended product name:** **SETU** (Sanskrit/Hindi: "bridge") — *AI-Powered Disaster Early Warning, Impact Assessment & Transparent Relief Bridge*. It bridges (a) official forecasting agencies → local administration, (b) predicted risk → resource need, and (c) donors/warehouses → verified delivery on the ground.

**One-line pitch:** *"SETU doesn't replace IMD, CWC or NDMA — it takes their official data, tells a district officer in one number how many people and which hospitals/roads are at risk in the next 6–24 hours, tells them exactly how much food/water/medicine to move from which warehouse, and gives every citizen and auditor a tamper-evident trail proving the relief actually arrived."*

---

## 2. PROBLEM DECONSTRUCTION

The PS statement bundles six distinct sub-problems. Treat them separately — this is also how you should structure PPT slides and judge answers.

| Sub-problem | Real-world pain point | Who owns it today | What SETU actually adds |
|---|---|---|---|
| **Early warning** | Warnings exist (CWC, IMD, NDMA's SACHET) but are agency-siloed, station-level, and not translated into "who is affected" | CWC (river levels), IMD (rainfall/cyclone), NDMA (SACHET CAP alerts) | Fuses official feeds into one hyperlocal risk score per village/ward, with a defined lead time and confidence |
| **Impact assessment** | No single layer tells a district officer *which population, hospitals, roads* sit inside a specific predicted hazard polygon, fast | Partially covered by NRSC's post-event flood mapping (Bhuvan-Flood), which is largely event-driven, not predictive/pre-event | GIS overlay of the *predicted* hazard zone (not just post-event satellite imagery) against population/infra layers, computed before the water arrives |
| **Resource requirement estimation** | Relief quantities are often decided ad hoc / by experience, not a standard, auditable formula | District administration, SDMA, NGOs individually | A transparent, adjustable, standards-based formula (Sphere Handbook-anchored) that anyone can audit |
| **Resource allocation** | Which warehouse sends what, to where, is a manual coordination problem across NGOs/government | District Collector's office, SDRF, NGOs | An optimization engine suggesting least-cost/fastest feasible allocation, always human-approved |
| **Relief tracking** | Once dispatched, there is limited real-time, tamper-evident visibility into where relief actually went | Ad hoc — paper trails, WhatsApp, spreadsheets | Structured status pipeline with immutable timestamps |
| **Transparency / accountability** | Diversion, duplication and corruption allegations are common in relief distribution; citizens and auditors have no independent verification | CAG/auditors post-facto, often months later | Near-real-time, cryptographically verifiable, publicly auditable (non-PII) ledger of allocation→delivery |

**What SETU must NOT claim to do:** issue official cyclone/flood warnings in place of IMD/CWC, replace NDMA's SACHET alerting, generate its own satellite imagery pipeline in place of ISRO/NRSC, or guarantee delivery (blockchain records a transaction; it does not move a truck).


---

## 3. EXISTING SYSTEMS & GAP ANALYSIS

### 3.1 What already exists in India (do not rebuild these)

| Agency/System | What it actually does | Access model | Gap SETU fills |
|---|---|---|---|
| **NDMA — SACHET (National Disaster Alert Portal)** | Common Alerting Protocol (CAP)-based pan-India alert dissemination via SMS/app/geo-intelligence | Public app + SMS (header XX-NDMAEW) | SACHET pushes alerts; it does not compute *who/what* is affected or *how much relief* is needed, nor track relief logistics |
| **CWC — National Flood Forecasting Network + C-FLOOD + FloodWatch India app** | Real-time river level/discharge monitoring at 332 stations, 5–7 day advisory forecasts (aff.india-water.gov.in), and new 2-D hydrodynamic C-FLOOD system giving village-level inundation forecasts for 3 basins so far | Public web portal, official app | Station/basin-level water forecasts, not population-impact or relief-logistics decisions; C-FLOOD currently covers only 3 river basins nationally, leaving most basins on the older statistical (gauge-to-gauge) method |
| **ISRO/NRSC — Bhuvan-Disaster, NDEM** | Satellite-derived flood/landslide/cyclone/drought/fire mapping, largely event-triggered (post/during-event imagery), National Database for Emergency Management | Public geoportal (Bhuvan), restricted NDEM login for official users | Mostly reactive/observational (what happened), not fused into a forward relief-allocation and tracking workflow |
| **IMD** | Rainfall, cyclone track, weather forecasting; official warning issuer | Public data + APIs (limited), forecast bulletins | SETU consumes IMD outputs as an input feature, never re-issues weather forecasts |
| **State/District Disaster Management Authorities (SDMA/DDMA)** | On-ground command, evacuation, relief coordination, shelter management | Manual/paper + informal digital tools (WhatsApp, spreadsheets) | This is exactly the operational layer SETU's dashboard and allocation engine is built *for* |
| **NDRF/SDRF** | Physical rescue operations | N/A | Out of scope — SETU is a decision/logistics layer, not a rescue-ops tool |

### 3.2 Non-government / global reference systems

| Existing System | What It Does | Limitation | Our Improvement |
|---|---|---|---|
| Google Flood Hub / Global Flood Awareness System (GloFAS) | ML + hydrological river-flood forecasting, global coverage | Coarse resolution for India, no relief-logistics or verification layer | We fuse official Indian station data at finer local resolution and connect prediction → logistics → verified delivery in one pipeline |
| GDACS (Global Disaster Alert & Coordination System) | Global multi-hazard alerting for rapid-onset disasters | Global/aggregate, not district-actionable, no relief tracking | Local, actionable, GIS-overlaid, with allocation + blockchain verification |
| Existing NGO/UN humanitarian logistics tools (e.g., LMMS, various ERP-style relief trackers) | Track relief distribution and beneficiary registration | Siloed per-organization, not interoperable across government + multiple NGOs, no independent public audit trail | Shared, permissioned ledger across all participating orgs with citizen-facing, non-PII audit view |
| Generic supply-chain blockchain pilots (e.g., IBM Food Trust-style) | Prove blockchain traceability works for physical goods logistics | Not disaster-specific, not integrated with prediction/GIS | Same trust mechanism, purpose-built for the disaster relief chain and tied directly to predicted-need data |

**Where our true innovation lies:** not in prediction accuracy (CWC/IMD/ISRO already do this at national scale and better than a student model ever could) and not in "inventing blockchain traceability" (a known pattern). The innovation is **cross-system orchestration**: turning official, fragmented, agency-siloed forecasts into one hyperlocal actionable number, wiring that number directly into a resource-estimation formula and an allocation engine, and closing the loop with independently verifiable delivery — end-to-end, in one pipeline, which today does not exist as a single integrated system in the public domain for Indian disaster relief. **Do not claim "no existing solution exists" in absolute terms** — claim instead that no single integrated, open, cross-agency orchestration + transparency layer exists at the district-operational level, which is a defensible, narrower claim.


---

## 4. PROPOSED PRODUCT

**Name:** SETU — *AI-Powered Disaster Early Warning, Impact Assessment & Transparent Relief Bridge*

**Positioning statement:** *A decision-support and transparency orchestration platform that fuses official Indian forecasting data (IMD/CWC/NRSC) with GIS impact modeling, standards-based relief estimation, and a permissioned-ledger verification trail — for district disaster officers, NGOs and citizens.*

### 4.1 Users and what each does

| User | Sees | Can do | Provides | Decides |
|---|---|---|---|---|
| **District Disaster Officer / DDMA** | Live risk map, predicted-affected population/infra, relief-requirement estimate, allocation recommendation, shipment status, audit trail | Approve/override AI recommendations, trigger public alert (with authority), approve allocation, resolve disputes | Ground-truth corrections, local warehouse inventory, approval decisions | Final call on all high-stakes actions (warnings, large allocations) |
| **SDMA / State nodal officer** | State-wide aggregated dashboard across districts | Cross-district resource reallocation, policy parameter configuration (e.g., per-person ration norms) | State inventory data, policy thresholds | State-level allocation between districts |
| **NGO / Relief Organization** | Assigned relief requests, allocation tasks, dispatch instructions | Accept/dispatch shipments, upload delivery proof (GPS/photo/OTP), raise disputes | Warehouse stock, delivery confirmations | Field-level dispatch routing within approved allocation |
| **Field Officer / Volunteer (mobile, offline-capable)** | Assigned delivery tasks, checklist | Confirm receipt/delivery with QR/OTP/geotag, flag discrepancies | On-ground verification data | None (execution role) |
| **Warehouse Manager** | Inventory levels, incoming allocation orders | Update stock, mark dispatched | Stock counts | Which specific batch/vehicle fulfills an order |
| **Citizen / Public** | Public alert level for their area, anonymized verified-relief-distribution summary (e.g., "12,400 relief kits verified delivered in District X") | Report last-mile issues (optional citizen-feedback channel) | Optional feedback/complaints | None |
| **Government Auditor (CAG-style) / Judge/Evaluator** | Full immutable audit trail, discrepancy log, KPI dashboard | Query any transaction's full history | — | Flags for investigation |
| **Donor (future scope)** | High-level verified-impact dashboard | Track where a contribution's equivalent resources were verified-delivered | Contribution records | — |


---

## 5. PRODUCT REQUIREMENTS DOCUMENT (PRD)

### 5.1 Product Vision
Give every level of India's disaster-response chain — from a district officer to a citizen — one trustworthy, auditable view that turns official early-warning data into predicted local impact, into a costed relief plan, into a verified delivery record, without replacing any existing government forecasting authority.

### 5.2 Problem Statement
District-level disaster response today is fragmented across agencies (forecast vs. GIS vs. relief logistics vs. accountability), largely manual below the state level, and lacks an independently verifiable trail from "relief was allocated" to "relief was received," which erodes public trust and slows response.

### 5.3 Target Users
District Disaster Officers, SDMA/DDMA staff, NGOs/relief organizations, field volunteers, warehouse managers, citizens, government auditors. (Full detail in Section 4.)

### 5.4 User Personas (representative, 3 of the ~8 users)
- **Rina, District Disaster Management Officer, flood-prone district:** Manages evacuation and relief prep during monsoon; today relies on phone calls and WhatsApp groups from CWC/IMD bulletins; needs one screen that already answers "who is at risk and what do I need to move where."
- **Anand, NGO Field Coordinator:** Coordinates 3-4 relief vehicles per event; struggles with duplicate/uncoordinated deliveries across NGOs to the same village while other villages are missed; needs a shared allocation view.
- **Priya, State Auditor:** Reviews relief-fund utilization months after an event via paper records; wants a near-real-time, tamper-evident log to reduce reconciliation time and flag anomalies early.

### 5.5 User Stories (18)
1. As a district officer, I want to see predicted flood-risk zones 6–24 hours ahead so I can prioritize evacuation and relief pre-positioning.
2. As a district officer, I want the system to show me estimated affected population per zone so I don't have to manually cross-reference census data.
3. As a district officer, I want to see which hospitals, shelters and roads fall inside a predicted hazard zone so I can plan access routes.
4. As a district officer, I want an auto-generated relief requirement estimate (food/water/medicine/shelter) so I can validate it against available stock quickly.
5. As a district officer, I want an allocation recommendation (which warehouse sends what, where) so I don't have to manually coordinate across NGOs.
6. As a district officer, I want to approve or override every AI recommendation before it becomes an action, so I retain accountability.
7. As an NGO coordinator, I want to see confirmed allocation tasks assigned to my organization so I avoid duplicate delivery to the same village.
8. As an NGO field officer, I want to confirm delivery via QR/OTP/geotagged photo even with poor connectivity, so the record syncs once I'm back online.
9. As a warehouse manager, I want to update stock levels and see incoming allocation orders so I can prepare dispatches.
10. As a citizen, I want to see the current risk level for my area and a summary of verified relief distribution nearby, without seeing anyone's personal data.
11. As an auditor, I want to query the complete history of any relief transaction so I can investigate discrepancies without waiting for paper reconciliation.
12. As a state nodal officer, I want an aggregated multi-district dashboard so I can reallocate resources across districts during a large event.
13. As a district officer, I want to be notified when predicted risk crosses a threshold (GREEN→YELLOW→ORANGE→RED) so I know when to escalate.
14. As an NGO, I want to raise a dispute if a delivery is marked complete but did not actually happen, so discrepancies get investigated.
15. As a system administrator, I want to configure relief-per-person policy parameters (e.g., litres of water/day) so the estimation formula reflects current government/Sphere-aligned norms.
16. As a district officer, I want to see model confidence and false-alarm-rate history alongside every prediction, so I can calibrate trust in the system over time.
17. As a field volunteer without internet, I want to log a delivery offline and have it sync automatically when connectivity returns, so no data is lost in poor-connectivity zones.
18. As a judge/evaluator, I want to see a clear separation between real official data, historical-data-driven predictions, and demo-simulated components, so I can assess what's actually working.

### 5.6 Functional Requirements (by category)
- **Early Warning:** ingest IMD/CWC feeds → compute grid/village-level risk score → assign GREEN/YELLOW/ORANGE/RED → notify.
- **GIS:** overlay predicted hazard polygon with population/building/road/infrastructure layers → compute affected counts.
- **Impact Assessment:** accessibility analysis (which roads/routes remain usable) → priority-zone ranking.
- **Relief Estimation:** formula-driven per-category requirement (food/water/medicine/shelter/personnel) with configurable policy parameters.
- **Relief Allocation:** optimization engine recommending source warehouse → destination → quantity → route.
- **Blockchain:** record allocation/dispatch/delivery/verification events immutably; expose query API.
- **Verification:** multi-factor delivery confirmation (QR + geotag + recipient/officer confirmation).
- **Dashboard:** role-specific views (officer/NGO/citizen/auditor).
- **Notifications:** SMS/push/dashboard alerts by risk level.
- **Administration:** user/role management, policy-parameter configuration, warehouse/inventory management.
- **Analytics:** historical KPI trends (lead time, allocation efficiency, discrepancy rate).
- **Audit:** full immutable transaction history query, exportable reports.

### 5.7 Non-Functional Requirements
Reliability (graceful degradation if any upstream feed is down); Availability (target 99% during active-event windows for prototype; higher for production); Latency (risk score refresh within minutes of new upstream data, not real-time-trading-grade); Scalability (district → state → multi-state horizontally); Security (RBAC, encryption in transit/at rest); Privacy (no raw citizen PII on-chain, data minimization); Explainability (every AI output shows contributing factors, not a black-box number); Accessibility (multi-language, low-bandwidth-friendly UI); Offline capability (field app functions without connectivity, syncs later); Disaster resilience (system must not itself go down when the disaster it monitors damages local infrastructure — cloud-hosted, multi-region backup); Auditability (every state-changing action logged with actor+timestamp).

### 5.8 MVP Tiering
**Must Have (SIH MVP):** rainfall/river-level ingestion (historical + simulated live feed) → ML risk score for one district/river basin → GIS population/infra overlay → relief estimation formula → simple allocation suggestion (rule-based/greedy, not full MILP) → permissioned-blockchain record of allocation→dispatch→delivery → QR/OTP-based delivery verification → officer + NGO + public dashboards.
**Should Have:** full MILP/OR-Tools allocation optimization; multi-district view; SMS alerting integration; offline-first mobile app with sync.
**Could Have:** multi-hazard (cyclone/landslide) support; model explainability visualizations; dispute-resolution workflow UI.
**Future:** direct API integration with NDMA/SACHET and state ERP systems; IoT sensor ingestion; production-grade multi-state deployment; donor-facing impact dashboard.


---

## 6. DATA STRATEGY & ARCHITECTURE

### 6.1 Data inventory (representative — prioritized for flood, the recommended demo hazard)

| Dataset | Source | Format | Spatial Res. | Temporal Res. | Free/API | SIH-Prototype Fit |
|---|---|---|---|---|---|---|
| River water level/discharge, flood forecasts | CWC — India-WRIS / aff.india-water.gov.in / FloodWatch India app | Web portal, bulletins (no fully open public REST API for programmatic pull as of 2026 — screen-scraping/manual download typical) | Station-level (332 stations) | Near real-time, 3-hourly model runs, 5–7 day advisory | Free, no registration for portal viewing; **no confirmed open API** | **Use historical bulletins/archives for training; simulate a live feed for demo** |
| Rainfall (observed + forecast) | IMD (open data portal, limited public API), GPM/GSMaP (NASA/JAXA, used by CWC itself as model input) | NetCDF/CSV/gridded | ~0.25° grid (satellite products) | Daily/sub-daily | Free (GPM/GSMaP via NASA/JAXA portals); IMD has restricted-access historical data | Use GPM/GSMaP + IMD published bulletins for prototype |
| DEM (elevation/slope) | Bhuvan (ISRO, various resolutions), SRTM (NASA, 30m, global open) | Raster (GeoTIFF) | 30m (SRTM) / finer via Bhuvan for some regions | Static | Free, open download | Directly usable |
| Satellite optical/SAR imagery | Sentinel-1 (SAR, all-weather, flood-water detection) & Sentinel-2 (optical), via Copernicus Open Access Hub / ESA; Landsat via USGS EarthExplorer | GeoTIFF | 10m (Sentinel) | 5–12 day revisit | Free, open, registration required | Sentinel-1 SAR is the standard choice for flood extent because it penetrates cloud cover, unlike optical imagery — usable for validating predicted vs. actual inundation |
| Population | WorldPop (gridded, ~100m, free, open license), Census of India (village/ward level, free, some processing needed), GHSL (JRC, free) | Raster/CSV | 100m grid (WorldPop) / village (Census) | WorldPop annual estimates; Census decennial (use latest + growth-adjusted) | Free, open | WorldPop for grid-level population-at-risk math; Census for village-level ground-truth naming |
| Infrastructure (roads, hospitals, schools, shelters) | OpenStreetMap (OSM), Bhuvan thematic layers, data.gov.in (state-wise POI datasets) | Vector (GeoJSON/Shapefile) | Feature-level | Periodically updated (OSM community-driven) | Free, open (OSM under ODbL) | Directly usable; expect gaps in rural completeness — flag as a known limitation |
| Historical disaster events/losses | NDMA reports, EM-DAT (international disaster database, free for research), state disaster management reports | CSV/PDF | Event/district level | Historical archive | Free (EM-DAT requires registration) | Use for backtesting and demo narrative, not primary training signal |
| Relief consumption norms | Sphere Handbook (humanitarian minimum standards, free/open), state government relief manuals (e.g., SDRF/NDRF norms, state relief codes) | PDF/document | N/A | Static, periodically revised | Free, open | Directly usable as configurable policy defaults, e.g., 15 L water/person/day minimum per Sphere [Sphere Handbook] |

**Key point for judges:** CWC and IMD do **not** currently expose a fully open, documented public REST API for programmatic real-time pull as far as our research found — access is via web portals/bulletins/apps. This is a **real, stated constraint**, not something to gloss over: our prototype will (a) use their historical/archived bulletins and open satellite proxies (GPM/GSMaP rainfall, Sentinel-1 SAR) for training and backtesting, and (b) simulate a live feed for the demo using recorded historical event data replayed at accelerated time, clearly labeled **SIMULATED**. Production deployment would require a formal data-sharing MoU with CWC/IMD/NDMA — this is normal for government-integration systems and should be stated as a roadmap item, not hidden.

### 6.2 Dataset strategy
- **Training:** historical CWC bulletins/river-level archives + IMD/GPM rainfall history + Sentinel-1 SAR flood-extent labels (for a chosen basin, 5–10 years where available) + EM-DAT/NDMA historical event records for backtesting labels.
- **Live inference (SIH demo):** a recorded historical flood event (e.g., a real Assam/Bihar or chosen-basin flood) replayed as if live, with real rainfall/river-level values from that event — technically an accurate simulation, not fabricated numbers.
- **Demonstration location — recommended: a single well-instrumented flood-prone river basin/district.** Selection criteria: (1) CWC forecasting stations present, (2) historical flood frequency high enough to have multiple labeled events, (3) Sentinel-1 SAR coverage available, (4) WorldPop/Census data available, (5) reasonably well-mapped in OSM. **Strong candidates:** a district on the Brahmaputra (Assam — highest flood frequency in India, CWC's original FLEWS pilot region) or a Mahanadi-basin district in Odisha (also a C-FLOOD pilot basin, meaning official forecast data quality is highest there — good for demo credibility and a natural talking point: "we build on the same basin CWC's own C-FLOOD system already covers"). **Recommended: a Mahanadi-basin district, Odisha**, specifically because it lets the team credibly say "we ingest CWC/C-FLOOD-equivalent data for a basin where official real-time modeling already exists," strengthening the "decision-support layer, not replacement" narrative.


---

## 7. AI/ML ARCHITECTURE

### 7.1 Model comparison (do not default to LSTM/CNN)

| Model | Input | Output | Strength | Weakness | Data need | Suitability |
|---|---|---|---|---|---|---|
| Logistic Regression / Random Forest | Rainfall, river level, soil moisture, DEM-derived features | Risk probability (binary/multiclass) | Fast, interpretable, works with small/medium tabular data, easy to explain to judges | Ignores temporal sequence structure unless features engineered manually | Low–medium | **Excellent baseline** — use as Baseline model |
| XGBoost / LightGBM (gradient-boosted trees) | Same tabular features + engineered lag/rolling-window features | Risk probability / severity score | Strong tabular performance, handles missing data well, fast to train/tune, highly explainable via SHAP | Still needs manual temporal feature engineering; less natural for raw sequences | Medium | **Recommended Primary model** for SIH tabular risk-scoring |
| LSTM / GRU | Raw time-series of rainfall/river-level sequences | Risk probability or river-level forecast | Learns temporal dependencies automatically, good for sequence forecasting | Needs more data than a small student-collected dataset typically has; harder to explain to non-ML judges; prone to overfitting on short historical records | High | Reasonable **future/secondary model** once more historical data is aggregated, not the primary MVP model |
| CNN (spatial) | Gridded rainfall/DEM/imagery patches | Spatial hazard map | Captures spatial patterns (e.g., basin shape, terrain) | Needs large labeled spatial datasets, heavier compute, riskier for a 2-3 week build | High | Future scope for spatial hazard mapping, not MVP |
| ConvLSTM | Spatiotemporal grid sequences | Hazard evolution map over time | Best of both worlds for gridded forecasting | Very data- and compute-hungry, hardest to get right/validate in hackathon timeframe | Very high | Explicitly **not recommended for SIH MVP** — flag as future/production scope |
| Temporal Fusion Transformer | Multi-horizon multivariate time series | Probabilistic multi-horizon forecast with attention-based explainability | State-of-the-art for multi-horizon forecasting with built-in interpretability | Complex to implement/tune correctly in limited time; overkill for a single-basin MVP | High | Future scope, mention as a credible upgrade path (shows technical maturity to judges) |
| Physics-informed hybrid (e.g., simple hydrological rainfall-runoff model + ML residual correction) | Rainfall, catchment parameters + ML on residuals | River-level/flood-probability with physical grounding | Most defensible scientifically; mirrors what CWC itself does (hydrologic + hydrodynamic modeling) [CWC methodology] | Requires basic hydrology domain knowledge, more setup effort | Medium | Strong **future direction** to mention for production credibility |

### 7.2 Recommendation
- **Primary model (MVP):** **XGBoost/LightGBM classifier** producing a calibrated flood-risk probability, using engineered features (rainfall accumulation over 6/24/72h, river-level trend/rate-of-rise, antecedent soil moisture proxy, basin/terrain static features). Chosen because it is fast to train and validate on a realistically small student-collected historical dataset, is explainable via SHAP feature importance (directly answers "why did the model say HIGH risk"), and is the standard, defensible choice for tabular hydrometeorological risk scoring at this project scale.
- **Baseline model:** Logistic Regression / Random Forest, kept explicitly to demonstrate the primary model's lift over a simple baseline — judges will ask this.
- **Future/production model:** LSTM or Temporal Fusion Transformer once multi-year, multi-basin historical data is aggregated at production scale, potentially combined with a physics-informed hydrological model as CWC's own methodology does.

**Do not claim LSTM/CNN by default** — for a single-basin, limited-history student dataset, a well-engineered gradient-boosted tree model will very likely outperform and will be far more explainable than a deep sequence model, which is the technically correct and judge-defensible position.

### 7.3 What exactly the AI predicts
- **Target variable:** Probability that river/flood water level at a given monitored point exceeds the **CWC-defined "Warning Level"** within the prediction horizon (CWC already defines LOW/MODERATE/HIGH/EXTREME flood categories relative to Warning Level and Danger Level at each station [CWC categorization] — reusing this official taxonomy, rather than inventing a new one, is both scientifically grounded and immediately legible to any government evaluator).
- **Prediction horizon:** 6-hour and 24-hour probability (two separate model heads/thresholds), chosen because it's short enough to be a genuinely useful early-warning window and long enough to be learnable from rainfall/river-level lag features without requiring extremely dense real-time sensor networks.
- **Spatial unit:** village/ward-level (aggregated from the nearest CWC gauge station + DEM-based flood-extent modeling for the surrounding low-lying area), not raw grid cells — this is the unit district officers actually plan around.
- **Output format:**
```
Zone: Village X, District Y
Risk Score: 0.87
Severity: HIGH (per CWC Warning/Danger Level convention)
Expected Window: 6–12 hours
Model Confidence: 78% (validation-set calibration, not to be confused with probability itself)
Top Contributing Factors: 72h rainfall accumulation (+), river level rate-of-rise (+), upstream reservoir release (+)
```
This format is deliberately explainable, not a bare number — judges will ask "what is the AI actually predicting," and "a calibrated probability of exceeding CWC's own Warning Level, at village granularity, for two time horizons" is a precise, defensible answer.


---

## 8. MODEL TRAINING PIPELINE

```
Raw Data (CWC bulletins, IMD/GPM rainfall, Sentinel-1 SAR, DEM, historical events)
→ Cleaning (missing-station imputation, unit normalization, timestamp alignment)
→ Spatial Alignment (snap all sources to basin/village grid via DEM + gauge catchment mapping)
→ Temporal Windowing (rolling 6h/24h/72h rainfall accumulation, river-level rate-of-rise features)
→ Train/Validation/Test Split — TEMPORAL split by event/year, never random row split (prevents leakage: same flood event's hours must not appear in both train and test)
→ Model Training (XGBoost primary, LR/RF baseline)
→ Hyperparameter Tuning (cross-validation across multiple historical events, not just k-fold on rows)
→ Evaluation (see metrics below)
→ Calibration (Platt scaling / isotonic regression so "0.87" means what it says probabilistically)
→ Deployment (batch/near-real-time scoring service)
→ Monitoring (track prediction vs. actual outcome each event; alert on drift)
→ Retraining (scheduled after each monsoon season with new labeled events)
```

**Handling known pitfalls:**
- *Missing data:* forward-fill short gaps in river-level series; flag and exclude stations with prolonged outages rather than silently imputing across long gaps.
- *Class imbalance:* flood-exceedance events are rare relative to normal-flow hours — use class-weighted loss and evaluate with PR-AUC (not accuracy, which would be misleadingly high from predicting "no flood" always).
- *Spatial/temporal leakage:* split by event and by time, never shuffle rows randomly; ensure no village near a training-event village leaks correlated conditions into the test set for the same event window.
- *Concept drift:* land use, urbanization and river morphology change over years — scheduled retraining, monitored drift metrics.

**Metrics that matter (not just accuracy):**
- **Precision & Recall** (recall matters more here — missing a real flood is far costlier than a false alarm, so we explicitly tune the decision threshold to favor recall within an acceptable false-alarm budget)
- **PR-AUC** over ROC-AUC as the primary ranking metric, since the positive class (flood exceedance) is rare
- **Brier score / calibration curve** — because "0.87" must actually mean 87% empirically, not just rank correctly
- **False Alarm Rate** and **Missed-Event Rate**, reported explicitly and separately — these are the two numbers a disaster-management judge will ask about directly
- **Lead time achieved** — how many hours of genuine advance warning the model provides versus simply reacting to already-exceeded levels


---

## 9. GIS IMPACT ASSESSMENT

```
Predicted Hazard Zone (risk-scored village/ward polygons)
        +  DEM (low-lying extent modeling)
        +  Population (WorldPop grid + Census)
        +  Buildings/Roads (OSM)
        +  Hospitals/Schools/Shelters (OSM + Bhuvan POI layers)
        +  Critical Infrastructure
                ↓
        Spatial Overlay (vector-raster intersection)
                ↓
        Affected Population Estimate
                ↓
        Infrastructure Exposure List
                ↓
        Accessibility Analysis (which roads remain usable)
                ↓
        Priority Zone Ranking
```

**Tech choices:** PostGIS as the spatial database (production) / GeoPandas for prototyping and batch jobs; QGIS for manual validation/visual QA during development, not runtime; vector data (roads, POIs, admin boundaries) as GeoJSON/PostGIS geometries; raster data (DEM, population grids) processed with rasterio and clipped per predicted-hazard polygon; spatial indexing (GiST in PostGIS) for fast point-in-polygon queries at scale.

**Formulas/logic:**
- **Population at risk** = Σ (WorldPop grid cell population × fraction of cell area intersecting the predicted hazard polygon), summed per village, cross-checked against Census village population for sanity.
- **Buildings/infrastructure at risk** = count of OSM building/POI features whose geometry intersects the hazard polygon.
- **Roads affected** = total length (km) of OSM road segments intersecting the hazard polygon, categorized by road class (arterial vs. local) since arterial-road flooding matters more for evacuation planning.
- **Accessibility score** per shelter/hospital = shortest-path network distance from the affected zone centroid to the nearest unaffected facility, using a road-network graph with flooded segments removed (simple Dijkstra/A* on a NetworkX graph is sufficient for MVP; production would add live road-closure updates).
- **Priority score** (0–1) = weighted combination: `0.4 × normalized_population_at_risk + 0.3 × critical_infra_count_normalized + 0.2 × (1 − accessibility_score) + 0.1 × risk_probability`. Weights are **ASSUMPTION** values, explicitly configurable by district officers — this transparency (a visible, adjustable formula) is itself a selling point versus an opaque score.


---

## 10. RELIEF REQUIREMENT ESTIMATION

**Not a vague AI statement — a transparent, auditable formula**, anchored on the internationally recognized Sphere Handbook minimum humanitarian standards, which specify indicators such as a minimum of **15 litres of water per person per day** and defined food-energy/shelter/health benchmarks [Sphere Handbook / Sphere Association], adjusted by configurable government/state relief-code parameters where available.

```
Estimated Requirement (per category, per zone)
   = Affected Population
   × Severity Multiplier (from GIS priority score, range 1.0–1.5)
   × Expected Relief Duration (days, default policy value, e.g., 3 days initial relief)
   × Resource Requirement Per Person Per Day (policy-configurable, Sphere-anchored default)
   × Buffer Factor (default 1.1, i.e., 10% contingency — ASSUMPTION, configurable)
```

**Per-category defaults (policy-configurable, Sphere-anchored where applicable):**
- Drinking water: 15 L/person/day (Sphere minimum) [Sphere Handbook]
- Food: energy-sufficient ration per Sphere/government relief-code norms — exact kcal/ration composition should be pulled from the applicable **state relief manual** where the demo district is chosen, since India's SDRF/NDRF norms specify actual approved relief-kit compositions; treat the generic 2,100 kcal/person/day Sphere reference as the fallback default if state-specific norms are unavailable.
- Medicine/health: basic first-aid/ORS kit per affected household (not per person) — rule-based, not per-capita scaled.
- Shelter: per-household (not per-person) tent/shelter-kit count, using average household size from Census for the zone.
- Rescue personnel/transport/equipment: **not per-capita formula-driven** — this is capacity-planning territory (how many boats/vehicles per X affected population in inaccessible terrain), best handled as a **rule-based lookup table calibrated against historical relief operations for the chosen district**, not a continuous formula.

**Recommended approach: hybrid, not pure ML.** Use a transparent rule-based/parametric formula (above) as the core — because relief planners must be able to audit and override every number, and because there is no large enough labeled "correct relief quantity" historical dataset to train a supervised model on. Reserve ML for a narrow, well-scoped sub-task only if time permits: predicting the **severity multiplier** from historical damage-outcome data, not the whole requirement calculation. This is both more honest and more defensible to judges than claiming "AI decides relief quantities."


---

## 11. RELIEF ALLOCATION OPTIMIZATION

**Inputs:** available resources per warehouse, estimated demand per zone (from Section 10), warehouse locations, affected-zone locations, road accessibility (from Section 9's network graph with flooded segments removed), priority score, transport capacity per vehicle.

**Output:** an assignment: *which warehouse sends what resource, in what quantity, to which zone, via which route* — presented as a **recommendation requiring officer approval**, never an autonomous dispatch action.

**Algorithm choice:** Model as a **transportation/min-cost-flow problem** (a well-understood special case of Linear Programming), solved with **Google OR-Tools** (open-source, free, well-documented, realistic for a student team to implement correctly in the available time) — not a full Vehicle Routing Problem (VRP) for MVP, since VRP adds substantial modeling and solver complexity (time windows, vehicle capacity, multi-stop routing) that is not necessary to demonstrate the core allocation-optimization concept convincingly.

**Objective (mathematically):**

Minimize: `Σ_i Σ_j (distance_ij × cost_per_km × quantity_ij) + λ × Σ_j unmet_demand_j`

Subject to:
- `Σ_j quantity_ij ≤ supply_i` for each warehouse i (cannot send more than available stock)
- `Σ_i quantity_ij ≥ demand_j × fulfillment_target` for each zone j, where feasible (prioritized by priority_score_j so high-priority zones are filled first when total supply < total demand)
- `quantity_ij = 0` if no accessible route exists between i and j (accessibility constraint from Section 9)

This is a **min-cost transportation problem with a shortage penalty**, directly solvable with OR-Tools' linear solver or even `scipy.optimize.linprog` for the MVP scale (handful of warehouses, tens of zones) — genuinely implementable by a student team in days, not weeks, and mathematically transparent enough to defend live in front of judges (unlike a black-box heuristic).

**Recommended for SIH:** OR-Tools MILP for the core allocation, with a simple greedy fallback (assign nearest-accessible-warehouse-first by priority order) if the solver is unavailable/slow in a live demo — always label which one actually ran.


---

## 12. BLOCKCHAIN ARCHITECTURE

### 12.1 Comparison

| Factor | Ethereum (public) | Polygon (public L2) | Hyperledger Fabric (permissioned) | Recommendation |
|---|---|---|---|---|
| Cost | Real gas fees, unpredictable | Lower gas fees than mainnet Ethereum but still real transaction costs | No gas fees — participants run nodes, cost is infrastructure not per-tx | Fabric |
| Speed/Throughput | Low (public consensus overhead) | Higher than Ethereum L1 | Highest — benchmarks show Fabric with consistently higher throughput and lower latency than Ethereum under equivalent workloads [ScienceDirect 2025 benchmark study] | Fabric |
| Privacy | Public by default — all data visible to anyone | Public by default | Private channels + private data collections allow selective, need-to-know data sharing between specific participants [Kaleido/technical comparisons] | Fabric |
| Government suitability | Weak — public ledgers are a poor fit where participant identity, data sensitivity and regulatory compliance matter | Weak, same reasons | Strong — Fabric is the standard reference choice for "only approved participants" enterprise/government-consortium requirements, governed neutrally under the Linux Foundation [Guideflow/industry comparisons] | Fabric |
| Permissioned access | No — anyone can transact | No | Yes — built for it | Fabric |
| Auditability | Public but pseudonymous, hard to tie to real-world identity/roles | Same | Every participant is a known, identity-verified organization (government dept, NGO) — auditability is *stronger*, not weaker, because identity is bound to each transaction | Fabric |
| SIH prototype complexity | Moderate (Solidity + testnet wallets) | Moderate (same tooling, cheaper testnet) | Moderate-high initial setup (channels, MSP/identity config) but conceptually simpler once running, and avoids needing real/test cryptocurrency entirely | Fabric slightly higher setup cost, offset by being the *architecturally correct* choice |

### 12.2 Recommendation: Permissioned consortium blockchain — Hyperledger Fabric

**This is the single most important correction to your current PPT.** Ethereum/Polygon are public, permissionless-by-default ledgers built for anonymous, trust-minimized value transfer among strangers — a poor conceptual fit for a government-NGO relief consortium where every participant (District Administration, specific NGOs, warehouses) is a *known, vetted, identity-bound organization*, and where transaction data (allocation quantities, delivery status) should be visible to consortium members and auditors, not the entire public internet by default. A permissioned ledger (Hyperledger Fabric, or Polygon deployed as a private/permissioned instance as a documented middle-ground alternative) is both the architecturally correct choice and the one real government/enterprise supply-chain deployments actually favor for regulated, identity-bound workflows [Kaleido technical analysis; Guideflow 2025-26 enterprise blockchain comparison]. For a *citizen-facing* transparency layer, the system can additionally publish periodic non-sensitive, aggregated proofs (e.g., Merkle-root hashes of verified deliveries) to a public chain or public website — giving public verifiability without exposing the operational ledger itself. **If Fabric's setup complexity is judged too high for the remaining build time, the acceptable fallback is a private/permissioned Polygon (Supernet/Edge) deployment** — same trust logic, more familiar Solidity/EVM tooling for a student team — but Fabric remains the technically correct primary recommendation and should be the one presented as the target architecture, with the fallback disclosed honestly if used.

### 12.3 Why blockchain is needed at all here (and where it is NOT)
Blockchain is justified **specifically** for the relief-transaction trail because it is a genuine multi-party trust problem: government, multiple NGOs and warehouses do not fully trust each other's records, and a tamper-evident, jointly-witnessed log measurably increases confidence versus a single party's database. **Blockchain is explicitly NOT used for:** storing sensor/weather data (no multi-party trust problem — it's just data ingestion, a normal database is correct and cheaper), storing ML predictions (same reason), or storing population/GIS data (same reason, plus these are large binary/raster datasets wrong for a ledger). Putting these on-chain would be technically unjustified and is a common (and heavily critiqued) SIH mistake — **avoid it explicitly, and say so to judges.**


---

## 13. WHAT EXACTLY GOES ON-CHAIN

**On-chain (Hyperledger Fabric ledger):**
```
RecordID (allocation/dispatch/delivery event)
Disaster ID
Source Org ID (warehouse/government)
Destination Org ID (NGO/zone)
Resource Type + Quantity
Timestamp
Zone ID (reference only — not full GIS geometry)
Transaction Status (REQUESTED/APPROVED/ALLOCATED/DISPATCHED/IN_TRANSIT/DELIVERED/VERIFIED/DISPUTED)
Digital Signature of submitting org
Document/Photo Hash (SHA-256 of the geotagged delivery photo, OTP proof, etc. — not the file itself)
```

**Off-chain (PostgreSQL/PostGIS + object storage):**
- Raw sensor/weather/satellite data, ML model outputs and full prediction history, GIS layers and computed hazard polygons, population/infrastructure datasets, full-resolution delivery photos and documents (referenced by hash from the on-chain record), user PII (names, phone numbers), warehouse inventory detail.

**Why this split:** the ledger stores only what needs multi-party tamper-evidence and small, structured records (blockchain is expensive and slow for large/binary data); everything bulky, sensitive, or single-party-authoritative stays in a normal database, with a cryptographic hash on-chain linking the two — so anyone can verify a specific document/photo matches what was recorded without exposing the document itself publicly. IPFS or a similar content-addressed store is a reasonable **future** upgrade for the off-chain document layer (production scope) but a simple private object store (e.g., S3-compatible bucket) with hash references is sufficient and simpler for the MVP.

## 14. SMART CONTRACT (CHAINCODE) DESIGN

**Functions:**
```
createDisaster(disasterId, hazardType, basin, startTime)
createReliefRequest(zoneId, resourceType, quantity, priorityScore)
approveRequest(requestId, approverOrgId)          # requires DISTRICT_OFFICER role
allocateResource(requestId, warehouseId, quantity) # requires DISTRICT_OFFICER or SDMA role
dispatchResource(allocationId, vehicleId, dispatchTime)  # requires WAREHOUSE role
markInTransit(allocationId, gpsCheckpoint)
verifyDelivery(allocationId, proofHash, verifierOrgId)   # requires FIELD_OFFICER or NGO role + recipient confirmation
flagDiscrepancy(allocationId, reason, flaggedByOrgId)
resolveDispute(allocationId, resolutionNote, resolverOrgId)  # requires DISTRICT_OFFICER/auditor role
```

**Roles/permissions:** enforced via Fabric's MSP (Membership Service Provider) — each organization (District Admin, each NGO, each warehouse) is a distinct, certificate-identified member; chaincode logic checks the invoking identity's org/role before allowing a state transition (e.g., only a District Officer identity can call `approveRequest`).

**State machine:**
```
REQUESTED → APPROVED → ALLOCATED → DISPATCHED → IN_TRANSIT → DELIVERED → VERIFIED
                                                                    ↓
                                                              DISPUTED → INVESTIGATED → RESOLVED
```
Every transition emits a Fabric chaincode event (for dashboard real-time updates) and is permanently appended to the ledger with the invoking identity and timestamp — this event log **is** the audit trail; no separate "audit_logs" table needs to duplicate it for anything blockchain already recorded.


---

## 15. DELIVERY VERIFICATION

**Core truth judges will probe:** a blockchain record only proves *someone with valid credentials asserted delivery happened* — it does not, by itself, prove relief physically reached the recipient. SETU addresses this with **multi-factor verification**, not blockchain alone:

1. **GPS check** — field officer/NGO app captures device GPS at delivery time; system flags a mismatch if GPS location is far from the target zone.
2. **Geotagged photo** — photo of delivery (e.g., recipient with relief kit) with embedded GPS+timestamp metadata; only its hash goes on-chain, full image stored off-chain.
3. **Recipient confirmation (OTP or QR)** — an SMS-based OTP sent to a registered local contact (e.g., village head/ward officer, not necessarily every individual recipient, to keep this operationally realistic) or a printed QR code scanned by both deliverer and a local witness.
4. **Dual confirmation** — both the delivering NGO/officer AND an independent local official (or a second NGO, where available) must confirm before status moves to VERIFIED, not just the delivering party alone — this is the actual anti-fraud mechanism, since a single self-reporting party can lie but a matched independent confirmation is harder to fake.
5. **Discrepancy flagging** — any citizen, auditor or partner org can flag a VERIFIED record as disputed, triggering the DISPUTED→INVESTIGATED→RESOLVED chaincode flow with human adjudication.

**Explicit honest framing for judges:** *"Blockchain guarantees the record cannot be silently altered after the fact and shows exactly who asserted what and when. Physical-world assurance comes from combining that immutable record with GPS, photo evidence and independent dual confirmation — no digital system can make 100% delivery fraud physically impossible, and we do not claim it does."*

---

## 16. COMPLETE SYSTEM ARCHITECTURE

```
Data Sources (CWC/IMD archives+bulletins, GPM/GSMaP rainfall, Sentinel-1 SAR, DEM/SRTM, WorldPop, OSM, Sphere/state relief norms)
        ↓
Data Ingestion Layer (Python ETL jobs — batch pull/scrape/replay; Airflow or simple cron for MVP)
        ↓
Data Processing Layer (Pandas/NumPy cleaning, feature engineering, spatial alignment)
        ↓
AI/ML Layer (XGBoost risk-scoring service — FastAPI microservice, serves calibrated probability + SHAP explanation)
        ↓
GIS / Spatial Intelligence Layer (PostGIS + GeoPandas microservice — overlay, exposure, accessibility, priority score)
        ↓
Decision Engine (relief-requirement formula service, Section 10)
        ↓
Relief Optimization Engine (OR-Tools allocation microservice, Section 11)
        ↓
Backend APIs (FastAPI, REST + WebSocket for live dashboard updates)
        ↓
Database (PostgreSQL/PostGIS — operational + spatial data)
        ↓
Blockchain (Hyperledger Fabric network — allocation/dispatch/delivery/verification ledger, invoked via Fabric SDK from backend)
        ↓
Notification Layer (SMS gateway e.g. Twilio/MSG91, push notifications, dashboard alerts)
        ↓
Dashboards (React — District Officer, NGO, Public, Auditor views)
```

**Per-component spec (representative subset — full spec in a companion Architecture Document):**

| Component | Technology | Responsibility | Input | Output | API/Protocol |
|---|---|---|---|---|---|
| AI/ML service | Python, FastAPI, XGBoost, SHAP | Compute risk score per zone | Processed features | Risk score + confidence + explanation JSON | REST |
| GIS service | Python, FastAPI, GeoPandas, PostGIS | Compute exposure/priority | Hazard polygon + layers | Affected population/infra JSON, priority score | REST |
| Optimization service | Python, FastAPI, OR-Tools | Allocation recommendation | Supply, demand, accessibility graph | Allocation plan JSON | REST |
| Backend API gateway | FastAPI | Auth, orchestration, business logic | All service outputs | Unified API for frontend | REST + WebSocket |
| Blockchain service | Node.js/Python Fabric SDK | Submit/query chaincode transactions | Allocation/dispatch/delivery events | Transaction receipts, ledger queries | Fabric gRPC via SDK, wrapped as internal REST |
| Frontend | React + Tailwind, Leaflet/Mapbox for maps | Role-specific dashboards | Backend API | Rendered UI | HTTPS |
| Mobile field app | React Native (or PWA for MVP), offline-first local storage | Field verification, offline queueing | Officer/NGO input | Sync payloads | REST (queued/retried) |


---

## 17. DATABASE ARCHITECTURE (PostgreSQL/PostGIS — key tables)

| Table | Key fields | Relationships |
|---|---|---|
| `users` | id PK, org_id FK, role, name, phone, password_hash | belongs to `organizations` |
| `organizations` | id PK, name, type (GOV/NGO/WAREHOUSE), fabric_msp_id | — |
| `disasters` | id PK, hazard_type, basin, start_time, status | has many `predictions`, `affected_zones` |
| `locations` (zones) | id PK, name, geom (PostGIS geometry), admin_level | referenced widely |
| `sensor_readings` | id PK, station_id, variable, value, timestamp, source | many-to-one with `locations` |
| `weather_data` | id PK, location_id FK, rainfall, temp, timestamp, source | — |
| `predictions` | id PK, disaster_id FK, zone_id FK, risk_score, severity, horizon, confidence, model_version, timestamp | many-to-one `disasters`, `locations` |
| `affected_zones` | id PK, disaster_id FK, zone_id FK, population_at_risk, priority_score | — |
| `infrastructure` | id PK, zone_id FK, type (hospital/school/shelter/road), geom, source | — |
| `population` | id PK, zone_id FK, count, source (worldpop/census), year | — |
| `resources` | id PK, warehouse_id FK, resource_type, quantity, updated_at | — |
| `warehouses` | id PK, org_id FK, geom, capacity | — |
| `relief_requests` | id PK, disaster_id FK, zone_id FK, resource_type, quantity_estimated, status | — |
| `allocations` | id PK, request_id FK, warehouse_id FK, quantity, status, fabric_tx_id | mirrors on-chain record |
| `shipments` | id PK, allocation_id FK, vehicle_id, dispatch_time, route_geom | — |
| `deliveries` | id PK, shipment_id FK, delivered_at, gps_point, photo_hash | — |
| `verification_records` | id PK, delivery_id FK, verifier_org_id FK, otp_confirmed, dual_confirmed_by | — |
| `blockchain_transactions` | id PK, fabric_tx_id, record_type, related_id, submitted_by, timestamp | mirrors ledger for fast query |
| `audit_logs` | id PK, actor_id FK, action, entity, timestamp | app-level actions not already on-chain |

*(Full ER diagram with cardinalities to be produced as a dedicated diagram — see Section 33.)*

---

## 18. API ARCHITECTURE

```
POST   /auth/login
POST   /disasters
GET    /disasters/{id}
GET    /predictions/{zone_id}
GET    /risk-zones?disaster_id=
GET    /impact-assessment/{zone_id}
POST   /relief-request
POST   /allocation
POST   /allocation/{id}/approve
POST   /dispatch
POST   /delivery/verify
GET    /blockchain/transaction/{id}
POST   /dispute
GET    /audit/{allocation_id}
```
**Auth:** OAuth2/JWT with RBAC scopes per role (DISTRICT_OFFICER, NGO, WAREHOUSE, FIELD_OFFICER, AUDITOR, PUBLIC-read-only). **Protocol mix:** REST for standard CRUD/query; **WebSocket** for live dashboard updates (new predictions, allocation status changes); **MQTT** reserved as future scope for IoT sensor ingestion (lightweight pub/sub fits low-power field sensors) — not needed for MVP since MVP ingests via batch/API pulls, not raw sensor telemetry.

---

## 19. DASHBOARD ARCHITECTURE

- **Government/District Officer:** live map (Leaflet/Mapbox) with risk-zone overlay, active alerts, population/infra-affected panel, relief-requirement summary, allocation recommendation with one-click approve/override, shipment tracking map, full blockchain audit-trail viewer.
- **NGO:** assigned requests queue, allocation tasks, dispatch/delivery confirmation flow (mobile-friendly), discrepancy-flagging tool.
- **Public/Citizen:** current risk level for their area (GREEN–RED), a non-PII, aggregated "verified relief delivered" summary (counts only, no names/addresses), disaster alert history.
- **Auditor:** full transaction search, discrepancy log, KPI trend charts, exportable reports. Sensitive PII (recipient names/phones) is restricted to authorized roles only, never shown on the public dashboard — a hard rule, not a configuration option.


---

## 20. ALERTING SYSTEM

**Channels:** SMS (via a gateway like MSG91/Twilio — realistic for India, low-connectivity-friendly), dashboard, push notification (mobile app), email for institutional users; siren/IoT integration explicitly **future scope**.

**Risk levels (aligned to CWC's own Warning/Danger Level convention, not invented from scratch):**
- **GREEN:** risk score < 0.3 — routine monitoring.
- **YELLOW:** 0.3–0.6 — heightened monitoring, pre-position resources.
- **ORANGE:** 0.6–0.85 — prepare evacuation/relief dispatch, notify district officer directly.
- **RED:** > 0.85 or river level modeled to exceed CWC Danger Level — immediate action recommended.
(Thresholds are **ASSUMPTIONS**, explicitly configurable per district by SDMA policy.)

**Critical rule: SETU never auto-issues a public warning.** All ORANGE/RED classifications generate a **recommended alert draft** that requires District Officer approval before dissemination — this is a safety and accountability requirement (see Section 21), and also directly avoids the "AI falsely cries wolf / AI causes panic" objection judges will raise.

---

## 21. HUMAN-IN-THE-LOOP

```
AI Recommendation → Human Review → Approval → Action
```
**Mandatory human approval points:** issuing any public-facing warning; approving any relief allocation above a configurable threshold quantity; recommending evacuation; resolving delivery disputes. **Why:** AI outputs here are probabilistic and imperfect (see Section 7 metrics — false alarms and missed events are both possible); high-stakes actions with real safety/legal/financial consequences must remain under accountable human authority, both for genuine safety reasons and because no government agency would adopt a system that removes human sign-off from evacuation/warning decisions. This is a **feature to highlight proactively**, not a limitation to hide — it directly answers "what happens if the AI is wrong."

---

## 22. SECURITY & PRIVACY

**Threat model (selected critical items):**

| Threat | Mitigation |
|---|---|
| Fake/spoofed sensor or rainfall data | Source-authenticated ingestion (only pull from designated official endpoints/archives), sanity-range validation, anomaly flagging before it reaches the model |
| Compromised user account | MFA for DISTRICT_OFFICER/AUDITOR roles, short-lived JWTs, RBAC scoping |
| Malicious/compromised NGO account | Fabric MSP-based identity (org-level cryptographic identity, not just app passwords), dual-confirmation requirement for VERIFIED status limits unilateral fraud |
| Fraudulent delivery confirmation | Multi-factor verification (Section 15) — GPS+photo+dual confirmation, not single self-report |
| Blockchain key theft | Hardware/KMS-backed key storage for org identities in production; for MVP, encrypted key storage with access logging |
| API abuse/DoS | Rate limiting, WAF, API gateway throttling |
| GPS spoofing | Cross-check delivery GPS against network-derived location/photo metadata where feasible; flag large mismatches for review rather than silently trusting |
| Data poisoning / adversarial ML | Source-restricted ingestion (Section above), outlier detection on incoming features before scoring |
| Insider threats | Full audit logging of all admin actions, least-privilege RBAC, blockchain's immutability itself limits post-hoc record tampering by insiders |

**Privacy:** data minimization (no PII on-chain), encryption in transit (TLS) and at rest, RBAC-gated access to recipient-identifying data, public dashboard shows only aggregated non-PII counts.

---

## 23. OFFLINE / LOW-CONNECTIVITY DESIGN

- **Offline-first mobile field app** (React Native/PWA with local SQLite/IndexedDB store): field officers can log delivery verification (GPS+photo+OTP capture) entirely offline; data queues locally.
- **Store-and-forward sync:** queued records sync automatically when connectivity returns, with conflict resolution (server timestamp wins for status, but all queued records are preserved in an append-only local log first — no data loss even if sync fails repeatedly).
- **Edge inference (future scope):** a lightweight version of the risk model could run on a local device/edge server in a district office with intermittent connectivity, syncing predictions when possible — not required for MVP since the model runs centrally and district dashboards can cache the last-known risk state locally for offline viewing.
- **Queued blockchain transactions:** the backend queues Fabric transaction submissions if the blockchain network is temporarily unreachable, retrying with idempotent transaction IDs to avoid duplicate ledger entries.
- **Power/satellite delay resilience:** system degrades gracefully — if a data source (e.g., a CWC bulletin) is delayed, the dashboard explicitly shows "last updated X hours ago" rather than silently showing stale data as current; this honesty is itself a reliability feature.


---

## 24. FEASIBILITY ANALYSIS

| Dimension | Assessment | Key risk | Mitigation |
|---|---|---|---|
| **Technical** | Feasible for a student team at MVP scope (tabular ML + GIS overlay + permissioned ledger are all well-documented, open-source-tooled tasks) | Fabric setup complexity | Fallback to permissioned Polygon or a simplified single-org Fabric network for demo |
| **Economic** | Prototype cost near-zero (open data + free tiers); pilot/production costs are real but modest relative to typical govtech budgets (see Section 26) | Underestimating production cloud/SMS costs | Budget explicitly for SMS gateway and managed DB/cloud in pilot-phase costing |
| **Operational** | Requires district officers/NGOs to adopt a new tool during high-stress events | Low adoption if UI isn't dead-simple | Design for minimal clicks in crisis mode; pilot with one motivated district first |
| **Legal/Regulatory** | Handling citizen-adjacent data requires care (even aggregated); no official mandate to consume CWC/IMD data programmatically without an MoU | No open API confirmed for real-time CWC/IMD pull | State this explicitly as a pre-production requirement: formal data-sharing agreement with CWC/IMD/NDMA |
| **Data** | Historical training data assembled from public/free sources is genuinely obtainable, though CWC real-time feeds require MoU-level access, not just an anonymous API key | Data gaps for chosen basin | Choose demo basin partly *because* of confirmed data availability (Section 6.2) |
| **Infrastructure** | Standard cloud infra suffices for MVP; production would benefit from state-govt data-center hosting for sovereignty/latency | None severe | — |
| **Organizational** | Government/NGO consortium onboarding takes real institutional time | Slow adoption cycle | Pilot-first strategy, not "national rollout on day one" claims |
| **Deployment** | Cloud deployment (containerized microservices) is straightforward; Fabric network deployment across multiple real organizations is the hardest production step | Multi-org Fabric bootstrapping | Start pilot with 2-3 org nodes (District Admin + 1-2 NGOs), scale channel membership over time |

---

## 25. VIABILITY FRAMEWORKS (used selectively — not every framework fits a govtech, non-commercial-in-the-traditional-sense problem)

**Business Model Canvas (adapted for govtech):**
- *Customer segments:* State/District Disaster Management Authorities (primary), NGOs/humanitarian orgs (secondary), citizens (beneficiary, non-paying).
- *Value proposition:* faster, auditable, cross-agency relief coordination; reduced corruption/diversion risk; faster public trust recovery post-disaster.
- *Revenue/funding:* government procurement (state IT/disaster-management budgets), CSR partnerships (many corporates already fund disaster relief per NDMA's own corporate-sector engagement [NDMA]), potential multilateral/development-agency grant funding (World Bank/UN disaster-resilience programs) — **not a consumer-revenue product.**
- *Key partners:* SDMA/DDMA, NDRF/SDRF, established NGOs, warehouse/logistics partners, cloud provider (preferably one with a government/MeitY empanelment for eventual production use).

**TAM/SAM/SOM:** meaningful only loosely here since this is a public-sector decision-support tool, not a market-priced product — better expressed as **addressable scope**: 36 states/UTs, 700+ districts, with flood being India's most frequent disaster type; a realistic SOM for a pilot is **1 district, 1 river basin**, scaling to a full state's flood-prone districts over 2-3 years if the pilot succeeds. Present this as scope, not as a dollar TAM — a TAM slide risks looking commercially tone-deaf for a public-safety system.

**SWOT (brief):** *Strengths:* builds on, not against, existing official data; transparent, auditable formulas. *Weaknesses:* dependent on official data-sharing MoUs for full production access; six-person team cannot build state-scale infra alone. *Opportunities:* growing government digitization push (e.g., National Supercomputing Mission-backed C-FLOOD shows active government investment in exactly this space) [Deccan Herald]. *Threats:* institutional adoption inertia; data-access gatekeeping.

**Frameworks deliberately NOT forced:** PESTLE and full Porter's-style competitive analysis add little for a single-buyer (government) decision-support tool and would read as padding — mention briefly if a judge asks, don't build a slide around them.

---

## 26. COST ANALYSIS (approximate, INR, labeled as ASSUMPTION ranges)

| Phase | Cloud/Compute | Database | Blockchain | SMS/Notifications | Storage | Total (approx., monthly) |
|---|---|---|---|---|---|---|
| **Prototype (SIH)** | Free tier (Colab/local + one small cloud VM) | Free tier PostgreSQL (e.g., Supabase/Neon free tier) | Free (local/testnet Fabric network, self-hosted) | Free tier SMS sandbox (a few hundred test messages) | Free tier object storage | **~₹0–2,000/month** |
| **Pilot (1 district)** | ₹8,000–15,000 (small managed VM/K8s) | ₹3,000–6,000 (managed PostGIS) | ₹5,000–10,000 (hosted Fabric nodes across 2-3 orgs) | ₹5,000–15,000 (real SMS volume) | ₹1,000–3,000 | **~₹22,000–49,000/month** |
| **Production (state-scale)** | ₹1,00,000+ (scaled compute, multi-region) | ₹30,000+ | ₹40,000+ (multi-org Fabric network ops) | ₹50,000+ (state-wide SMS volume) | ₹20,000+ | **~₹2,40,000+/month** (order-of-magnitude ASSUMPTION, would need formal cloud-provider quoting) |

**Free/open components:** all datasets in Section 6 except any paid IMD/CWC data-sharing arrangement; XGBoost, GeoPandas, PostGIS, OR-Tools, Hyperledger Fabric — all open-source with no licensing cost. **Government infrastructure possibility:** production deployment could use MeitY/NIC empanelled cloud (e.g., NIC's own data centers) which would change this cost structure significantly and is the realistic production path, not a generic commercial cloud bill.


---

## 27. MVP DEFINITION FOR SIH (single hazard scenario: FLOOD)

| # | Component | Status |
|---|---|---|
| 1 | Historical rainfall/river-level input | **REAL** (public GPM/GSMaP + CWC published bulletins for the chosen basin) |
| 2 | "Live" rainfall/river input during demo | **SIMULATED** (real historical event data replayed at accelerated time) |
| 3 | AI risk prediction | **REAL** model (trained XGBoost on real historical data), run live on simulated feed |
| 4 | Risk map | **REAL** (computed from real model output, real GIS layers) |
| 5 | Population impact | **REAL** (WorldPop/Census overlay, real computation) |
| 6 | Infrastructure impact | **REAL** (OSM overlay, real computation) |
| 7 | Relief estimation | **REAL formula**, using **ASSUMPTION**-labeled default policy parameters where state-specific norms aren't sourced in time |
| 8 | Resource allocation | **REAL** OR-Tools optimization, run against **MOCKED** warehouse inventory data (synthetic but realistic quantities) |
| 9 | Blockchain transaction | **REAL** (actual Hyperledger Fabric network, actually recording actual transactions — not a UI mockup) |
| 10 | Delivery verification | **SIMULATED** (demo actors perform the QR/OTP/photo flow live, since an actual physical delivery can't happen in a demo) |
| 11 | Dashboards | **REAL** (fully functional UI reading real backend data) |

**We will never claim #2, #8's inventory data, or #10 are production-ready** — they are honest, clearly-labeled simulations of real-world inputs the production system would receive from live government feeds, real warehouse ERPs, and real field devices respectively.

---

## 28. DEMO SCENARIO (illustrative numbers — clearly demo-only)

> Heavy rainfall begins upstream in the chosen river basin (real historical event, replayed).
> → System ingests rainfall + river-level data (SIMULATED live feed from REAL historical values).
> → AI computes rising flood-exceedance probability — crosses ORANGE at hour 4, RED at hour 9 (illustrative).
> → System predicts high-risk zones with a 6–12 hour window, confidence ~80% (illustrative, from real model calibration curve).
> → GIS calculates **~18,000 people** potentially affected across 6 villages (illustrative demo number, computed live from real WorldPop overlay for the actual chosen zones — not fabricated, but presented as a demo run's output, not a validated real-world forecast).
> → System identifies **3 hospitals, 2 shelters, 12 km of roads** at risk (same — real computation on real infra data for the chosen zone, illustrative as a specific demo instance).
> → Relief engine estimates required food/water/medicine/shelter using the Sphere-anchored formula.
> → Optimization engine identifies the nearest accessible warehouse via OR-Tools.
> → District officer reviews and approves the allocation (human-in-the-loop, shown live).
> → Blockchain records the allocation (real Fabric transaction, real tx ID shown).
> → Shipment dispatched (simulated in demo).
> → QR/GPS/OTP confirms delivery (demo actor performs this live).
> → Blockchain records VERIFIED status.
> → Dashboard shows the complete, queryable audit trail end-to-end.

Every number in this walkthrough should be explicitly narrated as "this is our live demo run's output" — not implied to be a validated real-world flood forecast for that basin today.

---

## 29. KPIs / SUCCESS METRICS

| Category | KPI |
|---|---|
| AI | Precision, Recall, PR-AUC, False Alarm Rate, Missed-Event Rate, Lead Time (hrs), Calibration/Brier score |
| GIS | Population-estimate error vs. Census ground truth, spatial-overlay accuracy (% correct zone assignment) |
| Relief | Allocation efficiency (% demand fulfilled), shortage/surplus reduction vs. naive baseline, response-plan generation time |
| Blockchain | Transaction latency (ms), ledger query latency, discrepancy-detection rate, % of allocations with full audit trail |
| System | API p95 latency, uptime during demo/pilot window, horizontal scalability (districts supported per deployment) |

---

## 30. RISK REGISTER (selected top items)

| Risk | Probability | Impact | Mitigation | Backup |
|---|---|---|---|---|
| Insufficient/low-quality historical training data for chosen basin | Medium | High | Choose demo basin partly by confirmed data availability (Section 6.2); supplement with satellite-derived proxies | Fall back to a better-documented basin (e.g., Mahanadi, already a C-FLOOD pilot basin) |
| Inaccurate predictions / high false-alarm rate | Medium | High | Explicit calibration, conservative thresholding, human-in-the-loop for all warnings | Present model limitations honestly with measured FAR/miss-rate, not hidden |
| No confirmed open real-time API from CWC/IMD | High | Medium | Use historical archives + simulated live feed for MVP; roadmap a formal MoU for production | Clearly disclosed as a known constraint, not glossed over |
| Blockchain (Fabric) setup complexity exceeds team's remaining time | Medium | Medium | Start Fabric setup early (Week 1-2, Section 32); permissioned-Polygon fallback | Documented fallback architecture, disclosed if used |
| Internet/connectivity failure in real deployment | High (real-world) | High | Offline-first mobile field app, store-and-forward sync (Section 23) | — |
| Fraudulent delivery verification | Medium | High | Multi-factor + dual confirmation (Section 15) | Dispute/investigation workflow |
| Model drift over seasons/years | Medium (long-term) | Medium | Scheduled retraining, monitored drift metrics | — |
| Government integration difficulty (production) | High | Medium | Pilot-first strategy, position as decision-support not replacement | — |
| Team skill gaps (GIS/blockchain unfamiliar to some members) | Medium | Medium | Early skill-mapping (Section 34), pair less-experienced members with the domain owner | Simplify Fabric to single-channel MVP if needed |


---

## 31. DEVELOPMENT ROADMAP (Phase view — see Section 37 for week-by-week build order)

- **Phase 0 — Documentation:** PRD, lightweight SRS, architecture doc, data source register, threat-model summary (2-3 days).
- **Phase 1 — Data:** collect/clean historical rainfall, river-level, DEM, population, infra datasets for chosen basin; set up PostGIS.
- **Phase 2 — AI:** baseline (LR/RF) → primary (XGBoost) → evaluation/calibration → deploy as FastAPI service.
- **Phase 3 — GIS:** spatial overlay pipeline, exposure/priority computation.
- **Phase 4 — Relief:** requirement-estimation formula service; OR-Tools allocation service.
- **Phase 5 — Blockchain:** Fabric network setup (or Polygon fallback), chaincode, SDK integration.
- **Phase 6 — Backend:** API gateway, auth/RBAC, service orchestration.
- **Phase 7 — Frontend:** officer/NGO/public dashboards.
- **Phase 8 — Integration:** wire end-to-end pipeline, demo-data replay harness.
- **Phase 9 — Testing:** unit, integration, ML validation, chaincode tests, load/failure testing.
- **Phase 10 — Deployment:** cloud hosting, monitoring, demo rehearsal.

---

## 32. TEAM STRUCTURE (6-person team)

| Role | Responsibilities | Key deliverables | Depends on | Tech |
|---|---|---|---|---|
| **AI/ML Lead** | Feature engineering, model training/calibration, evaluation | Trained model + FastAPI scoring service | Data Eng's cleaned dataset | Python, XGBoost, scikit-learn, SHAP |
| **Data Engineer** | Data collection/ETL, PostGIS schema, data-quality checks | Clean, aligned dataset + populated DB | Raw sources (Section 6) | Python, Pandas, PostGIS, Airflow/cron |
| **GIS Engineer** | Spatial overlay pipeline, exposure/accessibility/priority computation | GIS microservice | DEM/population/infra data | GeoPandas, PostGIS, QGIS (dev-time), NetworkX |
| **Blockchain Engineer** | Fabric network + chaincode (or Polygon fallback), SDK integration | Working ledger + smart contract functions | Backend API contract | Hyperledger Fabric, Go/Node chaincode, Fabric SDK |
| **Backend Engineer** | API gateway, auth/RBAC, service orchestration, relief/optimization services | FastAPI backend + OR-Tools allocation service | All microservice outputs | Python, FastAPI, PostgreSQL |
| **Frontend/Product/DevOps** | Dashboards, deployment, demo orchestration, PPT/pitch coordination | React dashboards, deployed demo, presentation | Backend APIs | React, Leaflet, Docker, cloud hosting |

---

## 33. REQUIRED DOCUMENTATION — WHAT'S ESSENTIAL BEFORE CODING

**Essential before development starts:** PRD (Section 5), lightweight System Architecture Document (Section 16), Data Source Register (Section 6), API Specification skeleton (Section 18), Database Schema/ER diagram (Section 17), Smart Contract Specification (Section 14) — these prevent the team building against different mental models.

**Can be created during development (living documents):** SRS detail, Low-Level Design per microservice, ML Model Card, GIS Data Specification, Test Plan/Test Cases, Threat Model detail.

**Useful only for production, skip/stub for SIH:** Disaster Recovery Plan, full Security Design document, Data Protection/Privacy compliance plan (state the intent in the PRD, don't write a full compliance dossier for a hackathon). **Always needed regardless of stage:** User Stories (Section 5.5), Demo Script (Section 28), Research References (this document's citations).

---

## 34. GITHUB / SOFTWARE ENGINEERING STRUCTURE

```
setu/
├── docs/                  # PRD, architecture, data register, ADRs
├── data/                  # raw/ (gitignored), processed/, sample/ (small demo datasets committed)
├── ml/                    # training pipeline, model artifacts, evaluation notebooks
├── gis/                   # spatial pipeline, overlay logic
├── relief_engine/         # requirement estimation + OR-Tools allocation
├── blockchain/            # Fabric network config, chaincode, SDK client
├── backend/               # FastAPI gateway + services
├── frontend/              # React dashboards
├── mobile/                # offline-first field app
├── infrastructure/        # Docker, docker-compose, IaC (Terraform optional)
├── tests/                 # unit/integration/ML/chaincode tests, mirrored per module
├── scripts/                # demo-data replay harness, seed scripts
└── README.md
```
**Practices:** Git branching — `main` (stable/demo-ready), `dev`, feature branches per module (`feature/gis-overlay`); Conventional Commits (`feat:`, `fix:`, `docs:`); GitHub Issues for task tracking (labeled by module); `.env.example` committed, real secrets in `.env` (gitignored) and GitHub Actions secrets for CI; basic CI (lint + unit tests) via GitHub Actions; PR review required before merge to `main`.

---

## 35. TESTING STRATEGY

- **Unit:** feature-engineering functions, GIS overlay math, relief-formula calculations, chaincode functions (individually).
- **Integration:** full pipeline from ingested data → prediction → GIS → relief estimate → allocation → blockchain record.
- **ML testing:** hold-out event validation, calibration checks, regression tests against known historical events (backtesting).
- **GIS testing:** known-answer tests (e.g., a synthetic polygon with known population should return the known population).
- **Smart contract testing:** Fabric chaincode unit tests for each state transition, including invalid-role-rejection tests.
- **API testing:** contract tests (e.g., pytest + httpx) for every endpoint, including auth-failure cases.
- **Security testing:** basic RBAC bypass attempts, rate-limit verification.
- **Load testing:** concurrent prediction requests (Locust/k6) at a realistic district-scale load.
- **Failure testing:** simulate an upstream data-source outage and confirm graceful degradation (Section 23).

**Example acceptance test:** *"Given rainfall of 150mm/24h and a river-level rate-of-rise of 0.5m/hr at the reference gauge, the system produces a flood-risk output for all downstream zones within 5 seconds, correctly classified as at least ORANGE per the configured thresholds."*


---

## 36. CHALLENGE THE CURRENT PPT — SLIDE-BY-SLIDE

| Existing slide area | Keep | Remove | Modify | Add |
|---|---|---|---|---|
| Problem/title | Core PS framing | "AI predicts disasters" phrasing | Reframe as decision-support layer over NDMA/IMD/CWC | One-line positioning statement |
| Proposed solution | 4-pillar structure | — | Rename pillars to match Predict→Assess→Estimate→Allocate→Track→Verify exactly | Explicit "what we are NOT replacing" callout |
| Technical approach | Python/FastAPI/PostgreSQL stack | Default LSTM/CNN claim, default Ethereum/Polygon claim | XGBoost primary model with justification; Hyperledger Fabric primary with justification | Model comparison table, blockchain comparison table (condensed) |
| Feasibility & viability | — | Vague "highly feasible" claims | Replace with the labeled feasibility table (Section 24) | Cost table, MVP tiering, REAL/SIMULATED demo labeling |
| Impact & benefits | Scale-across-states ambition | "Eliminates corruption," "prevents disasters" claims | Reframe as "reduces reconciliation time," "increases delivery verifiability" | KPI table |
| Research references | — | Generic/blog sources | Replace with authoritative sources used here (CWC, NRSC/Bhuvan, NDMA, Sphere Handbook, peer-reviewed blockchain benchmarks) | Full reference list |

**Recommended structure — keep your proposed 5-section flow, it's good:** 1) Proposed Solution, 2) Technical Approach, 3) Feasibility & Viability, 4) Impact & Benefits, 5) Conclusion. Add a short **"What we are NOT claiming"** micro-slide right after Proposed Solution — this single slide preempts a large fraction of hostile judge questions.

---

## 37. RECOMMENDED PPT SLIDE-BY-SLIDE (condensed — full script available on request)

| # | Title | Key message | Judge Q likely | Answer |
|---|---|---|---|---|
| 1 | SETU — Problem | Relief coordination is fragmented across agencies with no shared, verifiable trail | "Doesn't NDMA already do this?" | "NDMA/CWC/IMD do forecasting and alerting; no single layer turns that into district-level relief logistics with verified delivery." |
| 2 | Proposed Solution + "What we're not claiming" | Decision-support + transparency layer, not a replacement | "Why not just use existing govt systems?" | "We orchestrate them — CWC/IMD data in, verified relief logistics out." |
| 3 | Technical approach — AI | XGBoost primary, justified over LSTM/CNN for this data scale | "Why not deep learning?" | See Section 7.2 justification. |
| 4 | Technical approach — GIS + Relief formula | Transparent, Sphere-anchored formula, not black-box | "How is relief quantity decided?" | See Section 10 formula, cite Sphere 15L/day standard. |
| 5 | Technical approach — Blockchain | Hyperledger Fabric, justified over Ethereum/Polygon | "Why not Ethereum?" | See Section 12 comparison table. |
| 6 | End-to-end architecture diagram | One pipeline, Predict→Assess→Estimate→Allocate→Track→Verify | "Can this scale?" | Microservices + horizontal scaling story. |
| 7 | Demo walkthrough with REAL/SIMULATED labels | Honest, labeled demo | "Is this real or fake?" | Walk through Section 27 table live. |
| 8 | Feasibility & cost | Labeled assumptions, real cost table | "What does this cost?" | Section 26 table. |
| 9 | Impact & KPIs | Measurable, not hand-wavy | "How do you measure success?" | Section 29 KPI table. |
| 10 | Conclusion + roadmap | Pilot-first path to production | "What's next after SIH?" | Section 37 build plan + Section 31 roadmap. |

---

## 38. REQUIRED ARCHITECTURE DIAGRAMS

1. Problem → Solution (agency fragmentation → orchestration layer)
2. End-to-end system architecture (Section 16 diagram, formalized)
3. Data pipeline (sources → ingestion → processing)
4. AI pipeline (Section 8 flow)
5. GIS impact-assessment flow (Section 9 flow)
6. Relief estimation formula diagram (Section 10)
7. Allocation optimization flow (Section 11, with the objective function shown)
8. Blockchain architecture (organizations/peers/channels)
9. Smart-contract state machine (Section 14)
10. User interaction / role architecture (Section 4 table as a diagram)
11. Deployment architecture (containers/services/cloud)
12. Disaster demo flow (Section 28 sequence, as a swimlane diagram)

*(These can be generated as inline diagrams during pitch prep — recommend building 3, 6, 9 and 12 first as they answer the most likely judge questions.)*


---

## 39. JUDGE Q&A (40 questions, categorized)

**Problem**
1. *Doesn't NDMA/CWC/IMD already solve this?* — They forecast/alert; no single layer converts that into district relief logistics with verified delivery (Section 3.1).
2. *What's your actual innovation?* — Cross-agency orchestration + verified transparency, not raw prediction accuracy (Section 3.2 conclusion).
3. *Why flood and not all four hazards?* — Flood has the best public data availability in India; other hazards are architecturally supported but future scope (Section 6.2, 27).
4. *Is this a research project or a deployable product?* — Positioned as pilot-deployable decision-support, with explicit production roadmap (Section 31).

**AI**
5. *Why XGBoost, not LSTM/CNN?* — Section 7.2: small student-collected historical dataset, explainability, speed.
6. *What exactly does the model predict?* — Section 7.3: calibrated probability of exceeding CWC's own Warning Level, per zone, per horizon.
7. *How accurate is it?* — Report PR-AUC/FAR/miss-rate from validation, not a single "accuracy %" number; never claim near-100%.
8. *What happens if the AI is wrong?* — Human-in-the-loop for all high-stakes actions (Section 21); FAR/miss-rate transparently tracked (Section 29).
9. *How do you validate the model?* — Temporal, event-based train/test split; backtesting against known historical floods (Section 8).
10. *How do you handle false positives/negatives?* — Threshold tuned toward recall within an acceptable FAR budget; both rates reported explicitly (Section 8).
11. *Could this model scale to other basins?* — Architecture yes (retrain per basin); accuracy depends on basin-specific data availability — stated honestly.
12. *What's your training data size?* — State actual number once basin is finalized; if small, explicitly acknowledge and explain mitigation (baseline model, calibration, conservative thresholds).

**Data**
13. *Where does your data come from?* — Section 6.1 table with sources.
14. *Do CWC/IMD have open APIs?* — No confirmed open real-time API found; we use historical archives + simulate live feed, with a stated MoU requirement for production (honest, stated constraint).
15. *Is your data legally usable?* — All listed sources are free/open (WorldPop, SRTM, Sentinel, OSM, EM-DAT); CWC/IMD real-time production access would need formal government MoU.
16. *How current is your population data?* — WorldPop annual estimates + Census cross-check, explicitly dated.
17. *What if a sensor/station fails?* — Section 8 missing-data handling; degrade gracefully, flag stale data rather than fabricate.

**GIS**
18. *How do you calculate affected population?* — Section 9 formula: grid-cell population × intersection fraction with hazard polygon.
19. *How accurate is your spatial data?* — OSM has known rural completeness gaps — stated as a limitation, not hidden.
20. *Raster or vector, and why?* — Population/DEM as raster, infra/roads as vector; both processed via GeoPandas/PostGIS (Section 9).

**Blockchain**
21. *Why blockchain at all — why not a normal database?* — Genuine multi-party trust problem for the relief transaction trail specifically (Section 12.3); not used elsewhere.
22. *Why Hyperledger Fabric, not Ethereum/Polygon?* — Section 12.1-12.2: permissioned, identity-bound, higher throughput, no gas fees, matches a known-participant government-NGO consortium.
23. *What exactly goes on-chain?* — Section 13: structured transaction records + hashes only, never raw sensor/GIS/PII data.
24. *How do you prevent garbage data from being written immutably?* — Off-chain validation/sanity-checks happen before any chaincode submission; only validated, role-authorized transactions reach the ledger.
25. *What if an NGO disputes a transaction?* — DISPUTED→INVESTIGATED→RESOLVED state machine with human adjudication (Section 14).
26. *How does blockchain handle a network partition/no internet?* — Queued, idempotent transaction submission with retry (Section 23).
27. *Isn't blockchain just a marketing buzzword here?* — No — it's scoped specifically to the one part of this problem (multi-party relief-transaction trust) where it's architecturally justified, and explicitly not used elsewhere (Section 12.3).

**Security**
28. *How do you prevent fraudulent delivery confirmation?* — Multi-factor + dual independent confirmation (Section 15); explicitly state this reduces but does not eliminate fraud risk.
29. *How do you secure blockchain keys?* — MSP-based org identity, KMS-backed storage in production (Section 22).
30. *What about GPS spoofing?* — Cross-checked against photo metadata/network location, flagged not blindly trusted (Section 22).

**Feasibility/Scalability/Cost**
31. *Can a 6-person student team actually build this in the hackathon timeframe?* — Yes, at the explicitly scoped MVP tier (Section 27); full production is a multi-phase roadmap, not a hackathon claim.
32. *How much would this cost to run?* — Section 26 labeled cost table.
33. *How does this scale to all of India?* — Pilot → district → state → multi-state, gated by data-sharing MoUs and institutional adoption, not a "day one national rollout" claim (Section 25).

**Government adoption**
34. *How will this integrate with government systems?* — API-based integration point proposed, MoU-based data sharing for production (Section 24), not assumed automatic.
35. *Who will actually use and pay for this?* — SDMA/DDMA as primary users/budget holders, NGOs as participants (Section 25 Business Model Canvas).
36. *Has any government agency endorsed this?* — Honestly: no, this is currently a hackathon prototype; production requires formal government partnership — do not overclaim endorsement.

**Innovation/Demo**
37. *What can you actually demonstrate today?* — Section 27 REAL/SIMULATED/MOCKED table, presented transparently.
38. *What's simulated vs real in your demo?* — Same table — walk through it directly, this builds credibility rather than undermining it.
39. *What's your single biggest technical risk?* — Confirmed real-time CWC/IMD data access for production (Section 30 risk register) — state it plainly.
40. *What would you build next if given 3 more months?* — Multi-hazard support, LSTM/TFT upgrade path once more data is aggregated, formal government MoU pursuit, full offline mobile app (Section 27 "Future").


---

## 40. CLAIMS WE SHOULD NOT MAKE

| Avoid | Use instead |
|---|---|
| "100% accurate prediction" | "Calibrated probability with reported precision/recall/false-alarm-rate, validated by backtesting on historical events" |
| "Prevents disasters" | "Reduces response time and improves preparedness through earlier, more localized warning" |
| "Eliminates corruption" | "Increases traceability and auditability of relief distribution, reducing opportunity for undetected diversion" |
| "Guarantees delivery" | "Provides tamper-evident, multi-factor-verified evidence of delivery" |
| "Predicts every disaster" | "Provides short-horizon flood-risk probability for the modeled basin(s), scoped explicitly to flood in this MVP" |
| "Replaces government systems (NDMA/IMD/CWC)" | "Sits on top of and orchestrates official government data into district-level decision support" |
| "Real-time integration with NDMA/CWC" (if not actually confirmed) | "Designed for real-time integration pending formal data-sharing agreement; MVP uses historical/archived data" |
| "Blockchain makes this fraud-proof" | "Blockchain makes tampering with the recorded transaction history detectable; physical-world fraud resistance comes from multi-factor verification, not the ledger alone" |
| "AI decides relief allocation" | "AI/optimization recommends allocation; a human officer approves every action" |

---

## 41. FINAL RECOMMENDED ARCHITECTURE (single answer, not alternatives)

- **AI stack:** Python, XGBoost (primary) + Logistic Regression/Random Forest (baseline), scikit-learn, SHAP for explainability, served via FastAPI.
- **Data stack:** GPM/GSMaP + IMD rainfall archives, CWC historical bulletins, Sentinel-1 SAR, SRTM DEM, WorldPop + Census population, OSM infrastructure, Sphere Handbook + state relief-code norms; Pandas/NumPy for processing, Apache Airflow (or simple scheduled scripts for MVP) for orchestration.
- **GIS stack:** PostGIS (spatial database), GeoPandas (processing), QGIS (development-time validation only), Leaflet/Mapbox (frontend rendering), NetworkX (accessibility routing).
- **Backend:** FastAPI microservices behind an API gateway, REST + WebSocket.
- **Database:** PostgreSQL + PostGIS extension.
- **Blockchain:** Hyperledger Fabric (permissioned consortium), Fabric SDK (Node.js/Python) for backend integration; permissioned-Polygon deployment as the explicitly documented fallback if Fabric setup risk materializes.
- **Optimization:** Google OR-Tools (linear/min-cost-flow solver) for allocation.
- **Cloud:** any standard container-friendly cloud (e.g., a managed Kubernetes/VM offering) for prototype/pilot; NIC/MeitY-empanelled government cloud as the realistic production target.
- **Frontend:** React + Tailwind, Leaflet/Mapbox for maps, React Native or PWA for the offline-first field app.
- **Notifications:** SMS gateway (MSG91/Twilio-class provider) + push notifications + dashboard alerts; MQTT reserved for future IoT ingestion.
- **Security:** JWT/OAuth2 + RBAC, MFA for high-privilege roles, TLS everywhere, Fabric MSP-based org identity, KMS-backed key storage in production.

**Why this is the right balance:** every component is either (a) the standard, well-documented, free/open-source choice a small team can realistically implement correctly in the available time, or (b) the architecturally correct choice for the specific trust/scale problem it solves (Fabric for multi-party trust, PostGIS for spatial queries, OR-Tools for a genuinely solvable optimization formulation) — not the flashiest option, but the one that survives a technical cross-examination.

---

## 42. FINAL BUILD PLAN — "BUILD THIS NOW"

*(Adapted for a ~4-week SIH grand-finale-style build sprint; compress to ~10-14 days if the timeline is shorter — drop "Should Have" items first.)*

**Week 1 — Foundation**
- Input: PS + this document. Task: finalize demo basin/district (Section 6.2), write PRD/architecture doc (Sections 5, 16), set up GitHub repo (Section 34), collect and clean core historical datasets (Section 6). Output: repo scaffolded, cleaned dataset v0, PRD signed off by whole team. **Definition of Done:** every team member can explain the chosen basin, the exact AI target variable, and why blockchain is scoped the way it is.

**Week 2 — Core engines**
- Input: cleaned dataset, PostGIS schema. Task: train/evaluate baseline + XGBoost model (Section 7-8); build GIS overlay pipeline (Section 9); stand up Fabric network (or Polygon fallback) and chaincode (Section 12-14). Output: working model service, working GIS service, working ledger with test transactions. **DoD:** a script can take raw historical event data → produce a risk score → produce a population/infra-affected count, and a manual chaincode call successfully records and queries a transaction.

**Week 3 — Integration**
- Input: Week 2 services. Task: build relief-estimation + OR-Tools allocation service (Sections 10-11); build backend API gateway wiring all services (Section 16); build core dashboard views (Section 19). Output: end-to-end pipeline runs from replayed historical event → risk score → GIS impact → relief estimate → allocation recommendation → blockchain record, visible on a dashboard. **DoD:** the Section 28 demo scenario runs start-to-finish without manual intervention beyond the officer-approval clicks.

**Week 4 — Polish, verification flow, testing, pitch**
- Input: working end-to-end pipeline. Task: implement delivery-verification flow (Section 15); add public/auditor dashboards; run test suite (Section 35); rehearse demo with REAL/SIMULATED labeling (Section 27); finalize PPT (Sections 36-38) and judge Q&A prep (Section 39). Output: rehearsed, reliable demo + finished PPT + this document as the technical backup reference. **DoD:** the team can answer all 40 judge questions from memory, and the demo has run successfully at least 3 times without failure.

**Golden rule check:** by the end of Week 4, the team can answer, live, in front of a judge: *"Here is our real historical data, here is our real trained model with real (if imperfect) validation metrics, here is our real GIS computation, here is our real running blockchain network, here is exactly which parts are simulated and why, and here is our concrete plan to make the simulated parts real in a production pilot."* That is the win condition.

---

## RESEARCH REFERENCES

- NDMA — National Disaster Management Authority, https://ndma.gov.in/ ; SACHET National Disaster Alert Portal, https://sachet.ndma.gov.in/
- Central Water Commission — Flood Forecasting & Hydrological Observation, https://cwc.gov.in/flood-forecasting-hydrological-observation ; CWC Advisory Flood Forecast portal, https://aff.india-water.gov.in/ ; India-WRIS national flood forecasting network wiki
- "Centre unveils C-FLOOD, a unified flood forecasting system," Deccan Herald (CWC + C-DAC + NRSC, National Supercomputing Mission)
- ISRO/NRSC — Bhuvan Disaster Management Support Services, https://bhuvan-app1.nrsc.gov.in/bhuvandisaster/ ; NRSC Disaster Management applications, https://www.nrsc.gov.in/nrscnew/Apps_DMS.php
- Sphere Association — The Sphere Handbook: Humanitarian Charter and Minimum Standards in Humanitarian Response, https://spherestandards.org/handbook/
- Kaleido — "A Technical Analysis of Ethereum vs Fabric vs Corda," enterprise blockchain protocol comparison
- ScienceDirect (2025) — Performance comparison of permissioned and permissionless blockchain platforms (Hyperledger Fabric vs Ethereum benchmark study)
- Guideflow — "9 best blockchain platforms for 2026," enterprise blockchain platform comparison
- WorldPop (University of Southampton), Census of India, OpenStreetMap, Copernicus/ESA Sentinel-1/2, USGS SRTM/EarthExplorer, NASA/JAXA GPM-GSMaP — all as described in Section 6 data inventory.

*End of document. This is a working technical master plan — treat every numeric threshold and weighting formula marked ASSUMPTION as a starting point to refine once the team selects the final demo basin and reviews actual data availability.*
