from app.services.requirement_engine import compute_net_requirements


def test_net_requirement_subtracts_existing_inventory():
    results = {r.resource_type: r for r in compute_net_requirements(1000, 3, {"water_litres": 500})}
    water = results["water_litres"]
    assert water.gross_requirement == 3 * 3.0 * 1000  # WATER_LITRES_PER_PERSON_PER_DAY * days * population
    assert water.existing_inventory == 500
    assert water.net_requirement == round(water.gross_requirement - 500, 1)


def test_net_requirement_floors_at_zero_when_inventory_exceeds_gross():
    results = {r.resource_type: r for r in compute_net_requirements(10, 1, {"medical_kits": 999_999})}
    assert results["medical_kits"].net_requirement == 0.0


def test_missing_inventory_key_treated_as_zero_on_hand():
    results = {r.resource_type: r for r in compute_net_requirements(100, 3, {})}
    for r in results.values():
        assert r.existing_inventory == 0.0
        assert r.net_requirement == r.gross_requirement
