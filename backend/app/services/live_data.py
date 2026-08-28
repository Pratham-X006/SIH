"""
Real, working clients for free/no-key public disaster & weather data APIs.

These hit genuine third-party services over plain HTTPS. They will return real live data
on any machine with normal outbound internet access (your laptop, a cloud VM, a deployed
host). See docs/live_data_sources.md for why they could not be exercised live inside the
sandboxed container this scaffold was authored in.

Run this file directly for a quick manual smoke test:
    python -m app.services.live_data
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import httpx

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
USGS_EARTHQUAKE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
GDACS_RSS_URL = "https://www.gdacs.org/xml/rss.xml"

# Bounding box roughly covering mainland India, used to scope global feeds (USGS, GDACS).
INDIA_BBOX = dict(minlatitude=6.0, maxlatitude=37.0, minlongitude=68.0, maxlongitude=97.5)

DEFAULT_TIMEOUT = httpx.Timeout(15.0, connect=10.0)


@dataclass
class WeatherSignal:
    latitude: float
    longitude: float
    hourly_precipitation_mm: list[float] = field(default_factory=list)
    hourly_soil_moisture: list[float] = field(default_factory=list)
    daily_precipitation_sum_mm: list[float] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


async def fetch_weather_signal(lat: float, lon: float, forecast_days: int = 3) -> WeatherSignal:
    """Live rainfall + soil-moisture forecast for one point, from Open-Meteo (no API key)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "precipitation,soil_moisture_0_to_1cm",
        "daily": "precipitation_sum",
        "timezone": "Asia/Kolkata",
        "forecast_days": forecast_days,
    }
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(OPEN_METEO_FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    hourly = data.get("hourly", {})
    daily = data.get("daily", {})
    return WeatherSignal(
        latitude=lat,
        longitude=lon,
        hourly_precipitation_mm=hourly.get("precipitation", []),
        hourly_soil_moisture=hourly.get("soil_moisture_0_to_1cm", []),
        daily_precipitation_sum_mm=daily.get("precipitation_sum", []),
        raw=data,
    )


async def fetch_historical_rainfall(
    lat: float, lon: float, days_back: int = 365
) -> dict[str, Any]:
    """Real historical daily rainfall from Open-Meteo's archive API — used to train the
    baseline risk model on genuine (not synthetic) precipitation history."""
    end = date.today() - timedelta(days=2)  # archive has a short ingestion lag
    start = end - timedelta(days=days_back)
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "precipitation_sum,precipitation_hours",
        "timezone": "Asia/Kolkata",
    }
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(OPEN_METEO_ARCHIVE_URL, params=params)
        resp.raise_for_status()
        return resp.json()


async def fetch_recent_earthquakes(min_magnitude: float = 3.0, days_back: int = 30) -> list[dict]:
    """Live seismic events over India from USGS (no API key)."""
    start = (date.today() - timedelta(days=days_back)).isoformat()
    params = {
        "format": "geojson",
        "starttime": start,
        "minmagnitude": min_magnitude,
        **INDIA_BBOX,
    }
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(USGS_EARTHQUAKE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
    return data.get("features", [])


async def fetch_gdacs_alerts() -> str:
    """Raw GDACS multi-hazard RSS feed (floods, cyclones, quakes, volcanoes) — parse with
    any RSS/XML parser downstream. Returned raw here to keep this module dependency-light."""
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(GDACS_RSS_URL)
        resp.raise_for_status()
        return resp.text


async def fetch_all_live_signals(lat: float, lon: float) -> dict[str, Any]:
    """Fan out to all three sources concurrently for one dashboard refresh."""
    weather, quakes, gdacs_raw = await asyncio.gather(
        fetch_weather_signal(lat, lon),
        fetch_recent_earthquakes(),
        fetch_gdacs_alerts(),
        return_exceptions=True,
    )

    def _safe(result, empty):
        return empty if isinstance(result, Exception) else result

    return {
        "weather": _safe(weather, None),
        "earthquakes_count": len(_safe(quakes, [])),
        "earthquakes": _safe(quakes, []),
        "gdacs_raw_xml": _safe(gdacs_raw, ""),
        "errors": {
            "weather": str(weather) if isinstance(weather, Exception) else None,
            "earthquakes": str(quakes) if isinstance(quakes, Exception) else None,
            "gdacs": str(gdacs_raw) if isinstance(gdacs_raw, Exception) else None,
        },
    }


if __name__ == "__main__":
    # Manual smoke test — run locally where outbound internet is unrestricted:
    #   python -m app.services.live_data
    async def _main():
        result = await fetch_all_live_signals(lat=11.685, lon=76.132)  # Wayanad, Kerala
        print("Weather OK:", result["weather"] is not None, "| errors:", result["errors"])
        if result["weather"]:
            print("Next 3 daily rainfall totals (mm):", result["weather"].daily_precipitation_sum_mm)
        print("Earthquakes (30d, India bbox):", result["earthquakes_count"])

    asyncio.run(_main())
