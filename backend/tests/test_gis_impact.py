import pytest

from app.services import gis_impact


def test_unknown_district_raises():
    with pytest.raises(ValueError):
        gis_impact.assess_impact("Nonexistent District", 0.5)


def test_exposed_fraction_capped_at_one():
    result = gis_impact.assess_impact("Nagaon", risk_score=1.0)
    assert result["exposed_fraction"] <= 1.0
    assert result["estimated_exposed_population"] <= result["total_population_approx"]


def test_district_lookup_case_insensitive():
    assert gis_impact.find_district("nagaon") is not None
    assert gis_impact.find_district("NAGAON") is not None
