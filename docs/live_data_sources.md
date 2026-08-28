# Live data sources for the early-warning module

All three below are free and need **no API key or signup**, which is why they're wired up
first — you can go from zero to a live demo fastest with these. Endpoints actually used are
in `backend/app/services/live_data.py`.

## 1. Open-Meteo — rainfall, soil moisture, forecast + historical

- Forecast: `https://api.open-meteo.com/v1/forecast`
- Historical/archive (for model training): `https://archive-api.open-meteo.com/v1/archive`
- No key, no signup, generous free-tier rate limits, global coverage including all of India.
- Gives hourly precipitation, soil moisture (multiple depths), river-basin-relevant variables.
- This is the closest free substitute for the IMD rainfall + soil-moisture feeds named in the
  PPT's technical approach. IMD itself now runs a public API portal (`api.imd.gov.in`) but
  requires registration/approval — worth pursuing once the team has more time, listed as an
  upgrade path below.

## 2. USGS Earthquake API — real-time seismic events

- `https://earthquake.usgs.gov/fdsnws/event/1/query` (GeoJSON, no key)
- Global feed; filter by bounding box for India (`minlatitude=6&maxlatitude=37&minlongitude=68&maxlongitude=97`).
- Useful for the multi-hazard framing in the pitch (PS explicitly says the framework should
  extend beyond floods).

## 3. GDACS — Global Disaster Alert and Coordination System

- `https://www.gdacs.org/xml/rss.xml` (RSS) and a JSON GeoRSS variant is also published.
- Aggregates floods, cyclones, earthquakes, volcanic activity worldwide with a severity
  (green/orange/red) rating — good for a cross-hazard "situational awareness" panel on the
  dashboard alongside the flood-specific model.

## Upgrade path — India-specific official sources (need registration / longer lead time)

- **IMD API** (`api.imd.gov.in`) — official India Meteorological Department data; needs
  registration and approval, worth applying for early since hackathon timelines are tight.
- **India-WRIS / CWC** (`indiawris.gov.in`, `cwc.gov.in`) — river discharge and hydrological
  station data; primarily bulk/portal access today rather than a simple REST API, but is the
  most authoritative flood/river-gauge source and matches what the PPT cites.
- **Google Flood Hub API** (`developers.google.com/flood-forecasting`) — covers India, free,
  CC-BY-4.0 licensed, but requires a waitlist approval + Google Cloud project before you get
  an API key. Apply now if this is being pursued — approval lead time is unpredictable.
- **NASA FIRMS** (fire/thermal anomalies) — free, but needs a `MAP_KEY` via a quick
  self-service registration form.

## Important environment note

This scaffold was built inside a sandboxed cloud dev container whose outbound network is
allowlisted to a short list of package registries — it does **not** allow arbitrary calls to
third-party APIs like the ones above, so live calls could not be tested from inside that
container. This is a property of that one build environment, not of the code: run the same
`live_data.py` client from a normal machine (your laptop, a cloud VM, a deployed backend) and
it hits these APIs for real. Recommended before your first team demo: run
`python -m app.services.live_data` locally once (see the file's `__main__` block) to sanity
check the responses.
