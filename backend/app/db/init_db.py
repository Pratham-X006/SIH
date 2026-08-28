"""Create all tables and seed the static data-source provenance registry.
Run automatically on backend startup (see app/main.py) — idempotent (create_all + upsert-by-name).
"""
from __future__ import annotations

from app.db import models  # noqa: F401 - registers models on Base.metadata
from app.db.session import Base, SessionLocal, engine

DATA_SOURCE_REGISTRY = [
    dict(
        name="Open-Meteo Forecast API",
        category="REAL",
        source="Open-Meteo",
        url="https://api.open-meteo.com/v1/forecast",
        temporal_coverage="Live, rolling forecast window",
        spatial_coverage="Global (point query by lat/lon), including all of India",
        resolution="Point (nearest model grid cell, ~1-11km depending on region)",
        variables="hourly precipitation, hourly soil_moisture_0_to_1cm, daily precipitation_sum",
        processing="None — raw API response consumed directly by app/services/live_data.py",
        license="Open-Meteo free tier — no key required, attribution requested",
        limitations="Global reanalysis/forecast model, not an IMD station observation; "
        "treat as a documented proxy for official rainfall, not an IMD-equivalent reading.",
    ),
    dict(
        name="Open-Meteo Archive API",
        category="REAL",
        source="Open-Meteo",
        url="https://archive-api.open-meteo.com/v1/archive",
        temporal_coverage="Historical, from ~1940 to 2 days before present",
        spatial_coverage="Global (point query by lat/lon)",
        resolution="Daily aggregates (precipitation_sum, precipitation_hours)",
        processing="Rolling 1/3/7-day sums computed in app/ml/train.py; feature engineering "
        "only, no interpolation/imputation of missing days.",
        license="Open-Meteo free tier",
        limitations="Used to TRAIN the baseline risk model. The positive-class label is a "
        "documented heuristic (top-decile 3-day rainfall), not a ground-truth flood record — "
        "see MODEL_CARD.md.",
        variables="precipitation_sum, precipitation_hours",
    ),
    dict(
        name="USGS Earthquake Catalog",
        category="REAL",
        source="USGS",
        url="https://earthquake.usgs.gov/fdsnws/event/1/query",
        temporal_coverage="Live, rolling 30-day default window (configurable)",
        spatial_coverage="Global, filtered to an India bounding box in this system",
        resolution="Event-level (point + magnitude)",
        variables="magnitude, location, depth, time",
        processing="Bounding-box filter only",
        license="USGS public domain",
        limitations="Multi-hazard situational-awareness feed, not used by the flood risk model.",
    ),
    dict(
        name="GDACS Multi-Hazard RSS",
        category="REAL",
        source="GDACS (Global Disaster Alert and Coordination System)",
        url="https://www.gdacs.org/xml/rss.xml",
        temporal_coverage="Live feed",
        spatial_coverage="Global",
        resolution="Event-level",
        variables="hazard type, severity color (green/orange/red), location",
        processing="Raw XML passed through; not parsed into structured fields in this prototype",
        license="GDACS public feed",
        limitations="Situational-awareness only; not integrated into risk scoring or GIS overlay.",
    ),
    dict(
        name="District sample dataset (population/vulnerability)",
        category="DERIVED",
        source="Approximate figures referenced from public 2011 Census district summaries",
        url=None,
        temporal_coverage="2011 Census reference year, not adjusted for growth",
        spatial_coverage="6 named districts across Kerala, Assam, West Bengal, Odisha "
        "(see data/districts_sample.json)",
        resolution="District-level (single population figure + single vulnerability scalar)",
        variables="population_approx, vulnerability_index",
        processing="Hand-compiled from public Census summaries; vulnerability_index is an "
        "explicit judgment-call placeholder, not a sourced statistic.",
        license="Census of India data is public",
        limitations="Not village/ward-level, not WorldPop-grid-level. This is a stand-in for "
        "the WorldPop + OSM overlay pipeline described in the target architecture "
        "(ARCHITECTURE.md) — replace before any real deployment claim.",
    ),
    dict(
        name="Flood-risk heuristic label",
        category="DERIVED",
        source="Computed in app/ml/train.py from Open-Meteo Archive data",
        url=None,
        temporal_coverage="Matches whatever --days window train.py was run with",
        spatial_coverage="Single point per training run (lat/lon passed as CLI args)",
        resolution="Daily",
        variables="high_risk (binary)",
        processing="high_risk=1 if 3-day rolling rainfall >= 90th percentile of the pulled "
        "window for that point; see MODEL_CARD.md for why this is a proxy, not ground truth.",
        license="N/A (derived)",
        limitations="NOT a historical flood-occurrence record. Upgrading to real incident "
        "labels (state disaster authority archives, Sentinel-1 SAR flood extent) is the "
        "documented next step, not yet implemented in this build.",
    ),
    dict(
        name="Warehouses, inventory, allocations, deliveries (demo scenario)",
        category="SYNTHETIC",
        source="scripts/seed_demo.py",
        url=None,
        temporal_coverage="Generated at seed time",
        spatial_coverage="Same districts as the sample dataset",
        resolution="N/A",
        variables="org names, stock quantities, allocation records, one intentional discrepancy",
        processing="Procedurally generated for demo purposes",
        license="N/A",
        limitations="SYNTHETIC PROTOTYPE OPERATIONAL DATA. Not real government, NGO, or "
        "warehouse records. Never present as real in a demo or submission.",
    ),
    dict(
        name="Local Hardhat blockchain (ReliefTracking.sol)",
        category="SIMULATED",
        source="blockchain/ (Hardhat local network)",
        url=None,
        temporal_coverage="Ephemeral — resets whenever `npx hardhat node` restarts",
        spatial_coverage="N/A",
        resolution="N/A",
        variables="allocation lifecycle events (Allocated/Dispatched/Delivered/DiscrepancyFlagged)",
        processing="Real Solidity contract, real transactions, real tx hashes — but on a "
        "local, single-node development chain, not a public/consortium network.",
        license="N/A",
        limitations="Transactions are genuinely recorded and verifiable via the local chain's "
        "own ledger (this is real blockchain mechanics, not mocked), but there is no real "
        "multi-organization consortium network standing behind it yet — see BLOCKCHAIN.md.",
    ),
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_names = {row.name for row in db.query(models.DataSource).all()}
        for entry in DATA_SOURCE_REGISTRY:
            if entry["name"] not in existing_names:
                db.add(models.DataSource(**entry))
        db.commit()
    finally:
        db.close()
