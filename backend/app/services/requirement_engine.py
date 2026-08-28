"""Net requirement = gross requirement (relief_estimator.py) - existing local inventory
(spec Section 17). Kept as a thin wrapper rather than folded into relief_estimator.py so the
"gross" formula (population x norms) and the "net" step (subtract what's already on hand)
stay independently testable and independently explainable in the UI ("why this quantity?").
"""
from __future__ import annotations

from dataclasses import dataclass

from app.services.relief_estimator import estimate_relief

RESOURCE_UNITS = {
    "food_kg": "kg",
    "water_litres": "litres",
    "medical_kits": "kits",
    "shelter_units": "units",
}


@dataclass
class NetRequirement:
    resource_type: str
    unit: str
    gross_requirement: float
    existing_inventory: float
    net_requirement: float
    assumptions: dict


def compute_net_requirements(
    exposed_population: int, relief_days: int, existing_inventory: dict[str, float]
) -> list[NetRequirement]:
    gross = estimate_relief(exposed_population, relief_days)
    gross_by_resource = {
        "food_kg": gross.food_kg,
        "water_litres": gross.water_litres,
        "medical_kits": gross.medical_kits,
        "shelter_units": gross.shelter_units,
    }

    results = []
    for resource_type, gross_qty in gross_by_resource.items():
        on_hand = existing_inventory.get(resource_type, 0.0)
        net_qty = max(0.0, gross_qty - on_hand)
        results.append(
            NetRequirement(
                resource_type=resource_type,
                unit=RESOURCE_UNITS[resource_type],
                gross_requirement=gross_qty,
                existing_inventory=on_hand,
                net_requirement=round(net_qty, 1),
                assumptions={
                    "exposed_population": exposed_population,
                    "relief_days": relief_days,
                    "formula": f"gross_requirement ({gross_qty}) - existing_inventory ({on_hand}) "
                    f"= net_requirement ({round(net_qty, 1)})",
                    "gross_requirement_source": "app.services.relief_estimator (see that module's "
                    "docstring for the per-capita coefficients used)",
                    "existing_inventory_source": "SYNTHETIC PROTOTYPE OPERATIONAL DATA — sum of "
                    "resource_inventory rows for warehouses supplied to this call",
                },
            )
        )
    return results
