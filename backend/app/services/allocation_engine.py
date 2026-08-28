"""Resource allocation recommendation engine (spec Section 19 / masterplan Part 11).

Given one resource type's demand across a set of zones and the warehouses that stock it,
recommend WHAT/FROM/TO/QUANTITY/WHY. Two things this deliberately does NOT do:

1. It does not simply pick the nearest warehouse — any warehouse whose accessibility_score
   is below ACCESSIBILITY_INACCESSIBLE_THRESHOLD is excluded outright, and among the
   remaining feasible warehouses, cost is distance adjusted by accessibility, not raw
   distance alone (a road that's technically shorter but half-washed-out should lose to a
   longer clear route).
2. It never returns a bare list of numbers — every line item carries a human-readable
   `reasoning` string, and the final payload states which algorithm actually ran
   (`ortools_lp` or `greedy_fallback`), per the masterplan's "always label which one
   actually ran" rule. This is a recommendation for a human authority to approve
   (Section 19/69), never an autonomous dispatch action.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import ACCESSIBILITY_INACCESSIBLE_THRESHOLD, ALLOCATION_SHORTAGE_PENALTY_WEIGHT

try:
    from ortools.linear_solver import pywraplp

    _ORTOOLS_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised in envs without ortools installed
    _ORTOOLS_AVAILABLE = False


@dataclass
class WarehouseOption:
    warehouse_id: int
    warehouse_name: str
    stock_available: float
    distance_km: float
    accessibility_score: float  # 0=cut off, 1=fully accessible


@dataclass
class ZoneDemand:
    zone_id: int
    zone_name: str
    quantity_needed: float
    priority_score: float


@dataclass
class AllocationLine:
    warehouse_id: int
    warehouse_name: str
    zone_id: int
    zone_name: str
    resource_type: str
    quantity: float
    distance_km: float
    accessibility_score: float
    reasoning: str


@dataclass
class AllocationResult:
    resource_type: str
    method: str  # "ortools_lp" | "greedy_fallback"
    lines: list[AllocationLine] = field(default_factory=list)
    unmet_demand: dict[int, float] = field(default_factory=dict)  # zone_id -> unmet qty
    excluded_warehouses: list[dict] = field(default_factory=list)  # inaccessible, with why


def _effective_cost(distance_km: float, accessibility_score: float) -> float:
    # Guard against div-by-zero for a fully-inaccessible warehouse that somehow wasn't
    # filtered out upstream; such a case should never reach this function in practice.
    safe_accessibility = max(accessibility_score, 0.05)
    return distance_km / safe_accessibility


def _feasible_warehouses(
    warehouses: list[WarehouseOption],
) -> tuple[list[WarehouseOption], list[dict]]:
    feasible, excluded = [], []
    for w in warehouses:
        if w.accessibility_score < ACCESSIBILITY_INACCESSIBLE_THRESHOLD:
            excluded.append(
                {
                    "warehouse_id": w.warehouse_id,
                    "warehouse_name": w.warehouse_name,
                    "accessibility_score": w.accessibility_score,
                    "reason": f"accessibility_score {w.accessibility_score} is below the "
                    f"INACCESSIBLE threshold ({ACCESSIBILITY_INACCESSIBLE_THRESHOLD}) — "
                    f"excluded regardless of distance ({w.distance_km} km) or stock.",
                }
            )
        else:
            feasible.append(w)
    return feasible, excluded


def recommend_allocation(
    resource_type: str, zones: list[ZoneDemand], warehouses: list[WarehouseOption]
) -> AllocationResult:
    feasible, excluded = _feasible_warehouses(warehouses)

    if _ORTOOLS_AVAILABLE and feasible and zones:
        result = _solve_with_ortools(resource_type, zones, feasible)
        if result is not None:
            result.excluded_warehouses = excluded
            return result

    result = _solve_greedy(resource_type, zones, feasible)
    result.excluded_warehouses = excluded
    return result


def _solve_with_ortools(
    resource_type: str, zones: list[ZoneDemand], warehouses: list[WarehouseOption]
) -> AllocationResult | None:
    solver = pywraplp.Solver.CreateSolver("GLOP")
    if solver is None:  # pragma: no cover - environment without GLOP backend
        return None

    shipped: dict[tuple[int, int], object] = {}
    for w in warehouses:
        for z in zones:
            shipped[(w.warehouse_id, z.zone_id)] = solver.NumVar(
                0, solver.infinity(), f"ship_{w.warehouse_id}_{z.zone_id}"
            )
    unmet = {z.zone_id: solver.NumVar(0, solver.infinity(), f"unmet_{z.zone_id}") for z in zones}

    for w in warehouses:
        solver.Add(sum(shipped[(w.warehouse_id, z.zone_id)] for z in zones) <= w.stock_available)
    for z in zones:
        solver.Add(
            sum(shipped[(w.warehouse_id, z.zone_id)] for w in warehouses) + unmet[z.zone_id]
            == z.quantity_needed
        )

    objective = solver.Objective()
    for w in warehouses:
        for z in zones:
            objective.SetCoefficient(shipped[(w.warehouse_id, z.zone_id)], _effective_cost(w.distance_km, w.accessibility_score))
    for z in zones:
        objective.SetCoefficient(unmet[z.zone_id], ALLOCATION_SHORTAGE_PENALTY_WEIGHT * max(z.priority_score, 0.01))
    objective.SetMinimization()

    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:  # pragma: no cover - falls back on infeasibility
        return None

    lines: list[AllocationLine] = []
    for w in warehouses:
        for z in zones:
            qty = shipped[(w.warehouse_id, z.zone_id)].solution_value()
            if qty > 1e-6:
                lines.append(
                    AllocationLine(
                        warehouse_id=w.warehouse_id,
                        warehouse_name=w.warehouse_name,
                        zone_id=z.zone_id,
                        zone_name=z.zone_name,
                        resource_type=resource_type,
                        quantity=round(qty, 2),
                        distance_km=w.distance_km,
                        accessibility_score=w.accessibility_score,
                        reasoning=(
                            f"OR-Tools LP selected {w.warehouse_name} for {z.zone_name}: "
                            f"effective cost {round(_effective_cost(w.distance_km, w.accessibility_score), 2)} "
                            f"(distance {w.distance_km}km / accessibility {w.accessibility_score}), "
                            f"minimizing total effective transport cost plus a priority-weighted "
                            f"shortage penalty across all zones simultaneously."
                        ),
                    )
                )

    unmet_demand = {z.zone_id: round(unmet[z.zone_id].solution_value(), 2) for z in zones}
    return AllocationResult(resource_type=resource_type, method="ortools_lp", lines=lines, unmet_demand=unmet_demand)


def _solve_greedy(
    resource_type: str, zones: list[ZoneDemand], warehouses: list[WarehouseOption]
) -> AllocationResult:
    """Fallback: highest-priority zone served first, cheapest feasible (distance/accessibility
    adjusted) warehouse first within that zone. Used when ortools is unavailable/infeasible."""
    remaining_stock = {w.warehouse_id: w.stock_available for w in warehouses}
    zones_sorted = sorted(zones, key=lambda z: z.priority_score, reverse=True)
    lines: list[AllocationLine] = []
    unmet_demand: dict[int, float] = {}

    for z in zones_sorted:
        need = z.quantity_needed
        candidates = sorted(warehouses, key=lambda w: _effective_cost(w.distance_km, w.accessibility_score))
        for w in candidates:
            if need <= 1e-9:
                break
            available = remaining_stock[w.warehouse_id]
            if available <= 1e-9:
                continue
            qty = min(need, available)
            remaining_stock[w.warehouse_id] -= qty
            need -= qty
            lines.append(
                AllocationLine(
                    warehouse_id=w.warehouse_id,
                    warehouse_name=w.warehouse_name,
                    zone_id=z.zone_id,
                    zone_name=z.zone_name,
                    resource_type=resource_type,
                    quantity=round(qty, 2),
                    distance_km=w.distance_km,
                    accessibility_score=w.accessibility_score,
                    reasoning=(
                        f"Greedy fallback: {z.zone_name} ranked by priority_score={z.priority_score}; "
                        f"{w.warehouse_name} chosen as the lowest effective-cost feasible warehouse "
                        f"(distance {w.distance_km}km, accessibility {w.accessibility_score}) with "
                        f"remaining stock at allocation time."
                    ),
                )
            )
        if need > 1e-9:
            unmet_demand[z.zone_id] = round(need, 2)

    return AllocationResult(resource_type=resource_type, method="greedy_fallback", lines=lines, unmet_demand=unmet_demand)
