import pytest

from app.services.relief_estimator import estimate_relief


def test_zero_population_yields_zero_everything():
    e = estimate_relief(0, 3)
    assert e.food_kg == 0
    assert e.water_litres == 0


def test_scales_linearly_with_relief_days():
    e3 = estimate_relief(1000, 3)
    e6 = estimate_relief(1000, 6)
    assert e6.water_litres == pytest.approx(e3.water_litres * 2)


def test_rejects_negative_population():
    with pytest.raises(ValueError):
        estimate_relief(-1, 3)


def test_rejects_non_positive_days():
    with pytest.raises(ValueError):
        estimate_relief(100, 0)
