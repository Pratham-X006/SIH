import pytest

from app.services.geo_utils import haversine_km


def test_same_point_is_zero_distance():
    assert haversine_km(26.35, 92.68, 26.35, 92.68) == 0.0


def test_known_distance_delhi_to_mumbai_approx():
    # Great-circle distance Delhi <-> Mumbai is well-documented as ~1150-1160km.
    delhi = (28.6139, 77.2090)
    mumbai = (19.0760, 72.8777)
    distance = haversine_km(*delhi, *mumbai)
    assert 1100 < distance < 1200
