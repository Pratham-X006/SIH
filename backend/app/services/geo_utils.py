"""Geodesic distance only — the spec explicitly warns against computing distance/area from
raw latitude/longitude degree differences (they're not equal-length at different latitudes
or in different directions). Haversine great-circle distance is used here as a lightweight,
dependency-free geodesic calculation appropriate for warehouse-to-zone routing distances at
this prototype's scale; a production GIS pipeline would use PostGIS's geography type or a
proper road-network shortest path (see ARCHITECTURE.md) instead of straight-line distance.
"""
from __future__ import annotations

import math

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return round(2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a)), 2)
