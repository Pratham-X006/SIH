import pytest

from app.services.priority_engine import PriorityWeights, ZoneInput, compute_priorities


def test_empty_input_returns_empty():
    assert compute_priorities([]) == []


def test_higher_severity_population_and_deficit_ranks_first():
    high = ZoneInput(
        zone_id=1, zone_name="High", risk_level="severe", population_exposed=100_000,
        gross_requirement=1000, net_requirement=900, urgency=0.9, accessibility_score=0.5,
    )
    low = ZoneInput(
        zone_id=2, zone_name="Low", risk_level="low", population_exposed=1_000,
        gross_requirement=1000, net_requirement=100, urgency=0.2, accessibility_score=0.9,
    )
    results = compute_priorities([high, low])
    assert results[0].zone_name == "High"
    assert results[0].priority_score > results[1].priority_score
    assert results[0].explanation["rank"] == 1
    assert results[1].explanation["rank"] == 2


def test_population_norm_is_relative_to_batch_max():
    a = ZoneInput(zone_id=1, zone_name="A", risk_level="low", population_exposed=500, gross_requirement=10, net_requirement=0)
    b = ZoneInput(zone_id=2, zone_name="B", risk_level="low", population_exposed=1000, gross_requirement=10, net_requirement=0)
    results = {r.zone_name: r for r in compute_priorities([a, b])}
    assert results["B"].population_norm == 1.0
    assert results["A"].population_norm == 0.5


def test_resource_deficit_fraction_capped_and_floored():
    over_covered = ZoneInput(zone_id=1, zone_name="Z", risk_level="low", population_exposed=10, gross_requirement=100, net_requirement=0)
    fully_uncovered = ZoneInput(zone_id=2, zone_name="Y", risk_level="low", population_exposed=10, gross_requirement=100, net_requirement=100)
    results = {r.zone_name: r for r in compute_priorities([over_covered, fully_uncovered])}
    assert results["Z"].resource_deficit_norm == 0.0
    assert results["Y"].resource_deficit_norm == 1.0


def test_weights_are_configurable_and_affect_score():
    zone = ZoneInput(zone_id=1, zone_name="Z", risk_level="severe", population_exposed=100, gross_requirement=10, net_requirement=10, urgency=0.5)
    default_score = compute_priorities([zone])[0].priority_score
    urgency_only_weight = PriorityWeights(severity=0.0, population=0.0, resource_deficit=0.0, urgency=1.0, accessibility=0.0)
    reweighted_score = compute_priorities([zone], weights=urgency_only_weight)[0].priority_score
    assert reweighted_score == pytest.approx(0.5)  # only urgency term contributes now
    assert reweighted_score != default_score
