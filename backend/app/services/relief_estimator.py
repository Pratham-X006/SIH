"""Rule-based relief-requirement estimator. Fully functional — no external data or
placeholders. Per-capita coefficients are standard humanitarian-logistics rules of thumb
(rounded, conservative) and should be tuned against NDMA/SDMA relief-scale guidelines as the
team refines this module.
"""
from __future__ import annotations

from dataclasses import dataclass

# Per-affected-person daily coefficients (rounded rules of thumb — tune with real guidelines).
FOOD_KG_PER_PERSON_PER_DAY = 0.5
WATER_LITRES_PER_PERSON_PER_DAY = 3.0
MEDICAL_KITS_PER_1000_PEOPLE = 2.0
SHELTER_UNITS_PER_5_PEOPLE = 1.0  # one tent/shelter unit assumed to house ~5 people
RESCUE_PERSONNEL_PER_1000_AT_RISK = 3.0


@dataclass
class ReliefEstimate:
    exposed_population: int
    relief_days: int
    food_kg: float
    water_litres: float
    medical_kits: float
    shelter_units: float
    rescue_personnel: float


def estimate_relief(exposed_population: int, relief_days: int = 3) -> ReliefEstimate:
    if exposed_population < 0:
        raise ValueError("exposed_population cannot be negative")
    if relief_days <= 0:
        raise ValueError("relief_days must be positive")

    return ReliefEstimate(
        exposed_population=exposed_population,
        relief_days=relief_days,
        food_kg=round(exposed_population * FOOD_KG_PER_PERSON_PER_DAY * relief_days, 1),
        water_litres=round(exposed_population * WATER_LITRES_PER_PERSON_PER_DAY * relief_days, 1),
        medical_kits=round((exposed_population / 1000) * MEDICAL_KITS_PER_1000_PEOPLE, 1),
        shelter_units=round(exposed_population / (5 / SHELTER_UNITS_PER_5_PEOPLE), 1),
        rescue_personnel=round((exposed_population / 1000) * RESCUE_PERSONNEL_PER_1000_AT_RISK, 1),
    )
