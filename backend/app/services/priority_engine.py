"""Explainable zone-priority scoring (spec Section 18).

Deliberately NOT a black-box model: priority_score is a weighted sum of five named,
independently-inspectable terms, each traceable back to a real upstream number
(risk_level from the ML model, population_exposed from the GIS impact assessment,
net/gross requirement from the Relief Requirement Engine) or an explicit operator input
(urgency, accessibility) — see PriorityWeights in app/core/config.py for why each weight
has the value it does, and JUDGE_QA.md Q12 for the worked example this mirrors.

Population and resource-deficit terms are normalized *within one batch* (all zones being
compared for the same disaster), because "priority" is inherently relative — a zone with the
same population as every other zone shouldn't score as "0" for population, it should reflect
where it sits among the disaster's actual affected zones.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import SEVERITY_SCORE_BY_RISK_LEVEL, PriorityWeights, priority_weights


@dataclass
class ZoneInput:
    zone_id: int
    zone_name: str
    risk_level: str  # low | moderate | high | severe
    population_exposed: int
    gross_requirement: float
    net_requirement: float
    urgency: float = 0.5  # 0-1, ASSUMPTION default — no forecast-horizon feed in this prototype
    accessibility_score: float = 0.5  # 0=cut off, 1=fully accessible, ASSUMPTION default


@dataclass
class ZonePriorityResult:
    zone_id: int
    zone_name: str
    severity_score: float
    population_norm: float
    resource_deficit_norm: float
    urgency: float
    accessibility_score: float
    priority_score: float
    explanation: dict = field(default_factory=dict)


def _resource_deficit_fraction(z: ZoneInput) -> float:
    """Fraction of gross requirement still unmet after existing inventory is subtracted.
    0 = fully covered by existing stock, 1 = nothing covered yet."""
    if z.gross_requirement <= 0:
        return 0.0
    return max(0.0, min(1.0, z.net_requirement / z.gross_requirement))


def compute_priorities(
    zones: list[ZoneInput], weights: PriorityWeights = priority_weights
) -> list[ZonePriorityResult]:
    if not zones:
        return []

    max_population = max((z.population_exposed for z in zones), default=0) or 1
    results: list[ZonePriorityResult] = []

    for z in zones:
        severity_score = SEVERITY_SCORE_BY_RISK_LEVEL.get(z.risk_level, 0.5)
        population_norm = min(1.0, z.population_exposed / max_population)
        resource_deficit_norm = _resource_deficit_fraction(z)
        accessibility_penalty = 1.0 - z.accessibility_score

        score = (
            severity_score * weights.severity
            + population_norm * weights.population
            + resource_deficit_norm * weights.resource_deficit
            + z.urgency * weights.urgency
            + accessibility_penalty * weights.accessibility
        )

        explanation = {
            "terms": [
                {"factor": "severity", "value": severity_score, "weight": weights.severity,
                 "contribution": round(severity_score * weights.severity, 4),
                 "source": f"risk_level={z.risk_level!r} (from AI early-warning prediction)"},
                {"factor": "population_norm", "value": round(population_norm, 4), "weight": weights.population,
                 "contribution": round(population_norm * weights.population, 4),
                 "source": f"{z.population_exposed} exposed / {max_population} max-in-batch "
                            f"(from GIS impact assessment)"},
                {"factor": "resource_deficit_norm", "value": round(resource_deficit_norm, 4),
                 "weight": weights.resource_deficit,
                 "contribution": round(resource_deficit_norm * weights.resource_deficit, 4),
                 "source": f"net_requirement={z.net_requirement} / gross_requirement={z.gross_requirement} "
                            f"(from Relief Requirement Engine)"},
                {"factor": "urgency", "value": z.urgency, "weight": weights.urgency,
                 "contribution": round(z.urgency * weights.urgency, 4),
                 "source": "operator-supplied or default 0.5 — ASSUMPTION, no forecast-horizon "
                            "feed wired in this prototype"},
                {"factor": "accessibility_penalty", "value": round(accessibility_penalty, 4),
                 "weight": weights.accessibility,
                 "contribution": round(accessibility_penalty * weights.accessibility, 4),
                 "source": f"1 - accessibility_score({z.accessibility_score}) — operator-supplied "
                            f"or default 0.5, ASSUMPTION, no live road-network graph in this prototype"},
            ],
            "weights_used": weights.as_dict(),
        }

        results.append(
            ZonePriorityResult(
                zone_id=z.zone_id,
                zone_name=z.zone_name,
                severity_score=severity_score,
                population_norm=round(population_norm, 4),
                resource_deficit_norm=round(resource_deficit_norm, 4),
                urgency=z.urgency,
                accessibility_score=z.accessibility_score,
                priority_score=round(score, 4),
                explanation=explanation,
            )
        )

    results.sort(key=lambda r: r.priority_score, reverse=True)
    for rank, r in enumerate(results, start=1):
        r.explanation["rank"] = rank
    return results
