from app.services.allocation_engine import (
    WarehouseOption,
    ZoneDemand,
    _solve_greedy,
    recommend_allocation,
)


def test_inaccessible_warehouse_is_excluded_even_if_nearest():
    """The masterplan's explicit example: a 20km INACCESSIBLE warehouse must lose to a
    35km ACCESSIBLE one, not win on distance alone."""
    zones = [ZoneDemand(zone_id=1, zone_name="Z", quantity_needed=100, priority_score=0.8)]
    warehouses = [
        WarehouseOption(warehouse_id=1, warehouse_name="Near-Inaccessible", stock_available=1000, distance_km=20, accessibility_score=0.05),
        WarehouseOption(warehouse_id=2, warehouse_name="Far-Accessible", stock_available=1000, distance_km=35, accessibility_score=0.9),
    ]
    result = recommend_allocation("water_litres", zones, warehouses)
    assert len(result.excluded_warehouses) == 1
    assert result.excluded_warehouses[0]["warehouse_id"] == 1
    assert all(line.warehouse_id == 2 for line in result.lines)


def test_greedy_fallback_serves_highest_priority_zone_first_when_stock_is_scarce():
    zones = [
        ZoneDemand(zone_id=1, zone_name="LowPriority", quantity_needed=100, priority_score=0.2),
        ZoneDemand(zone_id=2, zone_name="HighPriority", quantity_needed=100, priority_score=0.9),
    ]
    warehouses = [WarehouseOption(warehouse_id=1, warehouse_name="Only", stock_available=100, distance_km=10, accessibility_score=1.0)]
    result = _solve_greedy("water_litres", zones, warehouses)
    assert result.lines[0].zone_id == 2  # HighPriority served first
    assert result.unmet_demand.get(1) == 100  # LowPriority gets nothing — stock exhausted


def test_stock_conservation_never_exceeded():
    zones = [ZoneDemand(zone_id=1, zone_name="Z", quantity_needed=1000, priority_score=0.5)]
    warehouses = [WarehouseOption(warehouse_id=1, warehouse_name="W", stock_available=300, distance_km=10, accessibility_score=1.0)]
    result = recommend_allocation("water_litres", zones, warehouses)
    total_shipped = sum(line.quantity for line in result.lines)
    assert total_shipped <= 300 + 1e-6
    assert result.unmet_demand[1] == 700


def test_method_is_always_labeled():
    result = recommend_allocation("water_litres", [], [])
    assert result.method in ("ortools_lp", "greedy_fallback")
    assert result.lines == []
