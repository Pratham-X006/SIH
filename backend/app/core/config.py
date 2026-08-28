"""Central, explicit policy configuration. Every tunable in the priority/allocation engines
lives here rather than buried in code, so an evaluator (or a district officer, in a real
deployment) can see and challenge every default. None of these weights are official
government standards unless stated — see docs/DATA_SOURCES.md and JUDGE_QA.md.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Anchored to backend/, not the process's current working directory — a relative sqlite:///
# URL would otherwise silently point to a different file depending on whether the backend
# was started from backend/ or a script was run from the repo root, which is exactly the
# kind of "same-looking but actually different database" bug this prototype must not have.
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_DEFAULT_DB_PATH = _BACKEND_DIR / "setu.db"


@dataclass
class PriorityWeights:
    """priority_score = severity*w_severity + population_norm*w_population
    + resource_deficit_norm*w_deficit + urgency*w_urgency + (1-accessibility)*w_accessibility

    Defaults are an ASSUMPTION, not a government-issued formula — deliberately mirrors the
    structure proposed in the project's own masterplan (Part 9.2 / mega-spec Section 18).
    Configurable via env vars so a district officer could retune without a code change.
    """

    severity: float = float(os.getenv("PRIORITY_W_SEVERITY", 0.30))
    population: float = float(os.getenv("PRIORITY_W_POPULATION", 0.25))
    resource_deficit: float = float(os.getenv("PRIORITY_W_DEFICIT", 0.25))
    urgency: float = float(os.getenv("PRIORITY_W_URGENCY", 0.10))
    accessibility: float = float(os.getenv("PRIORITY_W_ACCESSIBILITY", 0.10))

    def as_dict(self) -> dict[str, float]:
        return {
            "severity": self.severity,
            "population": self.population,
            "resource_deficit": self.resource_deficit,
            "urgency": self.urgency,
            "accessibility": self.accessibility,
        }


SEVERITY_SCORE_BY_RISK_LEVEL = {
    "low": 0.25,
    "moderate": 0.50,
    "high": 0.75,
    "severe": 1.00,
}

# Below this accessibility score (0=cut off, 1=fully open road access), a warehouse is treated
# as INACCESSIBLE and excluded from allocation entirely, regardless of distance/stock.
# ASSUMPTION default — no live road-closure feed exists in this prototype (see LIMITATIONS.md).
ACCESSIBILITY_INACCESSIBLE_THRESHOLD = float(os.getenv("ACCESSIBILITY_INACCESSIBLE_THRESHOLD", 0.20))

# Per-unit-distance shortage penalty ratio used by the allocation LP/greedy fallback: how many
# "distance units" of extra travel we're willing to accept to avoid leaving 1 unit of a
# high-priority zone's demand unmet. ASSUMPTION, configurable.
ALLOCATION_SHORTAGE_PENALTY_WEIGHT = float(os.getenv("ALLOCATION_SHORTAGE_PENALTY_WEIGHT", 1000.0))

DEMO_RELIEF_DURATION_DAYS = int(os.getenv("DEMO_RELIEF_DURATION_DAYS", 3))

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-insecure-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 8 * 60))

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_DEFAULT_DB_PATH}")

priority_weights = PriorityWeights()
