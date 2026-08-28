from fastapi import APIRouter, HTTPException

from app.services import live_data

router = APIRouter(prefix="/hazards", tags=["hazards"])


@router.get("/live")
async def get_live_hazards(lat: float, lon: float):
    """Live weather signal + regional earthquakes + GDACS multi-hazard feed for one point.
    Requires outbound internet to Open-Meteo/USGS/GDACS — see docs/live_data_sources.md."""
    result = await live_data.fetch_all_live_signals(lat, lon)
    weather = result["weather"]
    return {
        "location": {"lat": lat, "lon": lon},
        "weather": None
        if weather is None
        else {
            "daily_precipitation_sum_mm": weather.daily_precipitation_sum_mm,
            "hourly_precipitation_mm": weather.hourly_precipitation_mm,
            "hourly_soil_moisture": weather.hourly_soil_moisture,
        },
        "earthquakes_count_30d": result["earthquakes_count"],
        "earthquakes": result["earthquakes"],
        "gdacs_feed_available": bool(result["gdacs_raw_xml"]),
        "errors": {k: v for k, v in result["errors"].items() if v},
    }


@router.get("/earthquakes")
async def get_earthquakes(min_magnitude: float = 3.0, days_back: int = 30):
    try:
        return await live_data.fetch_recent_earthquakes(min_magnitude, days_back)
    except Exception as exc:  # noqa: BLE001 - surface upstream failure clearly
        raise HTTPException(status_code=502, detail=f"Live data fetch failed: {exc}") from exc
