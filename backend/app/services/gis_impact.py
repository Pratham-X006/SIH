"""Lightweight GIS impact assessment — deliberately dependency-light (no GDAL/geopandas)
so the skeleton installs fast. Combines a hazard risk score with the bundled sample district
dataset. See data/README.md: population/vulnerability figures here are sample seed data,
not live or authoritative — swap in a real dataset before treating outputs as real estimates.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "districts_sample.json"


@lru_cache
def _load_districts() -> list[dict]:
    with open(DATA_PATH) as f:
        return json.load(f)["districts"]


def find_district(name: str) -> dict | None:
    name_lower = name.strip().lower()
    for d in _load_districts():
        if d["name"].lower() == name_lower:
            return d
    return None


def list_districts() -> list[dict]:
    return _load_districts()


def assess_impact(district_name: str, risk_score: float) -> dict:
    """Estimate population and asset exposure for a district at a given hazard risk score.

    exposed_population = population * risk_score * vulnerability_index
    This is an intentionally simple, transparent formula for the hackathon-stage skeleton —
    a full model would use terrain/infrastructure layers (QGIS/GeoPandas, as in the pitch)
    rather than a single vulnerability scalar.
    """
    district = find_district(district_name)
    if district is None:
        raise ValueError(f"Unknown district: {district_name!r}. See data/districts_sample.json")

    exposed_fraction = min(1.0, risk_score * district["vulnerability_index"])
    exposed_population = round(district["population_approx"] * exposed_fraction)

    return {
        "district": district["name"],
        "state": district["state"],
        "hazard_focus": district["hazard_focus"],
        "risk_score": risk_score,
        "vulnerability_index": district["vulnerability_index"],
        "total_population_approx": district["population_approx"],
        "estimated_exposed_population": exposed_population,
        "exposed_fraction": round(exposed_fraction, 4),
    }
