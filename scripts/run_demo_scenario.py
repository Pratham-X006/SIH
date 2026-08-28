"""Drives the full PREDICT -> ASSESS -> ESTIMATE -> PRIORITIZE -> ALLOCATE -> TRACK -> VERIFY
-> AUDIT pipeline through the REAL running HTTP API (Section 48/49). Nothing here writes to
the database directly — every step is an actual API call, so what prints below is exactly
what a real client session produced, not a scripted fake trace.

Honesty note on the "historical flood" framing: this script feeds the risk model REAL,
LIVE rainfall for Nagaon, Assam (fetched from Open-Meteo at run time) — it does NOT replay
the specific 2018/2020 historical monsoon event, because that would require the Sentinel-1/
CWC historical-event pipeline described as a roadmap item in ARCHITECTURE.md/LIMITATIONS.md,
which is not yet built. What you see below is the real pipeline operating on real current
conditions, clearly labeled as such at each step.

Prerequisites (see DEMO.md):
  1. `python scripts/seed_demo.py` has been run at least once.
  2. Backend running: `uvicorn app.main:app --reload --port 8000` (from backend/)
  3. Local blockchain running + contract deployed (see README.md)

Usage:
    python scripts/run_demo_scenario.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

import httpx  # noqa: E402

from app.services.geo_utils import haversine_km  # noqa: E402

BACKEND_URL = "http://127.0.0.1:8000"
NAGAON = {"name": "Nagaon", "lat": 26.35, "lon": 92.68}
COMPARISON_ZONE = {"name": "Kamrup", "lat": 26.20, "lon": 91.75}

# ASSUMPTION accessibility scores — no live road-closure feed in this prototype (see
# LIMITATIONS.md). Chosen deliberately so the "nearer warehouse can lose to a farther,
# more accessible one" behaviour (Section 19) has something to demonstrate.
WAREHOUSE_ACCESSIBILITY = {
    "Kampur Forward Depot (near, flood-prone access road)": 0.30,
    "Guwahati Regional Warehouse (far, all-weather road)": 0.90,
    "Barpeta District Store": 0.70,
}


def _section(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def _die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def login(client: httpx.Client, username: str, password: str) -> str:
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    if resp.status_code != 200:
        _die(f"Login failed for {username}: {resp.status_code} {resp.text}. Run scripts/seed_demo.py first?")
    return resp.json()["token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def main() -> None:
    with httpx.Client(base_url=BACKEND_URL, timeout=20) as client:
        try:
            client.get("/health").raise_for_status()
        except httpx.HTTPError as exc:
            _die(f"Backend not reachable at {BACKEND_URL}: {exc}")

        officer_token = login(client, "district_officer", "demo-pass-1")
        warehouse_token = login(client, "warehouse_mgr", "demo-pass-2")
        relief_token = login(client, "relief_centre", "demo-pass-4")

        _section("STEP 1 — PREDICT: live weather signal + flood-risk prediction for Nagaon")
        live = client.get("/hazards/live", params={"lat": NAGAON["lat"], "lon": NAGAON["lon"]}).json()
        if live.get("errors"):
            print(f"  (some live sources failed: {live['errors']})")
        daily_rain = (live.get("weather") or {}).get("daily_precipitation_sum_mm") or [0]
        rain_24h = daily_rain[0] if daily_rain else 0.0
        rain_72h = sum(daily_rain[:3])
        rain_7d = sum(daily_rain)
        print(f"  LIVE (Open-Meteo) rainfall for Nagaon — 24h: {rain_24h}mm, 72h: {rain_72h}mm, 7d: {rain_7d}mm")

        risk = client.post(
            "/predict/flood-risk",
            json={"rain_24h_mm": rain_24h, "rain_72h_mm": rain_72h, "rain_7d_mm": rain_7d, "rain_intensity_max_mm_h": rain_24h / 4},
        ).json()
        print(f"  Risk score: {risk['risk_score']} | Risk level: {risk['risk_level']} | Model: {risk['model_source']}")

        _section("STEP 2 — ASSESS: GIS impact assessment (Nagaon vs. comparison zone Kamrup)")
        impact_nagaon = client.post("/impact/assessment", json={"district": NAGAON["name"], "risk_score": risk["risk_score"]}).json()
        impact_kamrup = client.post("/impact/assessment", json={"district": COMPARISON_ZONE["name"], "risk_score": max(0.1, risk["risk_score"] - 0.3)}).json()
        print(f"  {NAGAON['name']}: {impact_nagaon['estimated_exposed_population']} ESTIMATED POPULATION EXPOSED "
              f"(of {impact_nagaon['total_population_approx']} total, vulnerability_index={impact_nagaon['vulnerability_index']})")
        print(f"  {COMPARISON_ZONE['name']}: {impact_kamrup['estimated_exposed_population']} ESTIMATED POPULATION EXPOSED (comparison zone)")

        _section("STEP 3 — ESTIMATE: relief requirement engine (gross - existing inventory = net)")
        req_nagaon = client.post(
            "/api/requirements/calculate",
            json={"zone_name": NAGAON["name"], "exposed_population": impact_nagaon["estimated_exposed_population"], "relief_days": 3, "disaster_label": "NAGAON-FLOOD-DEMO"},
        ).json()
        for r in req_nagaon["requirements"]:
            print(f"  {r['resource_type']}: gross={r['gross_requirement']} - existing={r['existing_inventory']} = net={r['net_requirement']} {r['unit']}")

        req_kamrup = client.post(
            "/api/requirements/calculate",
            json={"zone_name": COMPARISON_ZONE["name"], "exposed_population": impact_kamrup["estimated_exposed_population"], "relief_days": 3, "disaster_label": "NAGAON-FLOOD-DEMO"},
        ).json()

        _section("STEP 4 — PRIORITIZE: explainable zone priority scoring")
        water_req_nagaon = next(r for r in req_nagaon["requirements"] if r["resource_type"] == "water_litres")
        water_req_kamrup = next(r for r in req_kamrup["requirements"] if r["resource_type"] == "water_litres")
        priorities = client.post(
            "/api/priorities/compute",
            headers=auth_headers(officer_token),
            json={
                "disaster_label": "NAGAON-FLOOD-DEMO",
                "zones": [
                    {"zone_name": NAGAON["name"], "risk_level": risk["risk_level"], "population_exposed": impact_nagaon["estimated_exposed_population"],
                     "gross_requirement": water_req_nagaon["gross_requirement"], "net_requirement": water_req_nagaon["net_requirement"],
                     "urgency": 0.8, "accessibility_score": 0.5},
                    {"zone_name": COMPARISON_ZONE["name"], "risk_level": "moderate", "population_exposed": impact_kamrup["estimated_exposed_population"],
                     "gross_requirement": water_req_kamrup["gross_requirement"], "net_requirement": water_req_kamrup["net_requirement"],
                     "urgency": 0.4, "accessibility_score": 0.7},
                ],
            },
        ).json()
        for p in priorities:
            print(f"  Rank {p['rank']}: {p['zone_name']} — priority_score={p['priority_score']}")
            for term in p["explanation"]["terms"]:
                print(f"      + {term['factor']}={term['value']} x weight={term['weight']} = {term['contribution']}")

        _section("STEP 5 — ALLOCATE: warehouse selection (not just nearest)")
        warehouses_resp = client.get("/api/warehouses").json()
        zone_demand_lines = []
        warehouse_options = []
        for w in warehouses_resp:
            distance = haversine_km(w["lat"], w["lon"], NAGAON["lat"], NAGAON["lon"])
            accessibility = WAREHOUSE_ACCESSIBILITY.get(w["name"], 0.5)
            warehouse_options.append({"warehouse_id": w["id"], "resource_type": "water_litres", "distance_km": distance, "accessibility_score": accessibility})
            print(f"  {w['name']}: {distance}km from Nagaon, accessibility_score={accessibility}")

        top_priority = priorities[0]
        zone_demand_lines.append({"zone_id": top_priority["zone_id"], "quantity_needed": water_req_nagaon["net_requirement"], "priority_score": top_priority["priority_score"]})

        recommendation = client.post(
            "/api/allocations/recommend",
            headers=auth_headers(officer_token),
            json={"resource_type": "water_litres", "zones": zone_demand_lines, "warehouses": warehouse_options},
        ).json()
        print(f"\n  Allocation method used: {recommendation['method']}")
        for line in recommendation["lines"]:
            print(f"  -> warehouse_id={line['warehouse_id']} sends {line['quantity']} water_litres to zone_id={line['zone_id']}")
            print(f"     WHY: {line['reasoning']}")
        for excl in recommendation["excluded_warehouses"]:
            print(f"  (excluded: {excl['warehouse_name']} — {excl['reason']})")

        if not recommendation["lines"]:
            _die("Allocation engine returned no lines — check seeded inventory levels.")

        _section("STEP 6 — Human approval + on-chain recording (VERIFIED path)")
        line = recommendation["lines"][0]
        approval = client.post(
            "/api/allocations/approve",
            headers=auth_headers(officer_token),
            json={
                "warehouse_id": line["warehouse_id"], "zone_id": line["zone_id"], "resource_type": "water_litres",
                "quantity": line["quantity"], "distance_km": line["distance_km"], "accessibility_score": line["accessibility_score"],
                "reasoning": line["reasoning"], "allocation_method": recommendation["method"],
            },
        ).json()
        print(f"  Allocation #{approval['allocation_id']} approved by district_officer. {approval['blockchain_note']}")

        client.post("/api/deliveries/dispatch", headers=auth_headers(warehouse_token), json={"allocation_id": approval["allocation_id"], "quantity_dispatched": line["quantity"]})
        print(f"  Dispatched {line['quantity']} water_litres.")

        confirm = client.post("/api/deliveries/confirm", headers=auth_headers(relief_token), json={"allocation_id": approval["allocation_id"], "quantity_received": line["quantity"]}).json()
        print(f"  Relief centre confirms receipt of {line['quantity']}. Result: {confirm['status']} ({confirm['blockchain_note']})")

        _section("STEP 7 — Second allocation, INTENTIONAL discrepancy (DISCREPANCY path)")
        food_req = next(r for r in req_nagaon["requirements"] if r["resource_type"] == "food_kg")
        food_warehouse_options = [
            {**opt, "resource_type": "food_kg"} for opt in warehouse_options
        ]
        food_recommendation = client.post(
            "/api/allocations/recommend",
            headers=auth_headers(officer_token),
            json={"resource_type": "food_kg", "zones": [{"zone_id": top_priority["zone_id"], "quantity_needed": min(food_req["net_requirement"], 5000), "priority_score": top_priority["priority_score"]}], "warehouses": food_warehouse_options},
        ).json()
        food_line = food_recommendation["lines"][0]
        food_approval = client.post(
            "/api/allocations/approve",
            headers=auth_headers(officer_token),
            json={
                "warehouse_id": food_line["warehouse_id"], "zone_id": food_line["zone_id"], "resource_type": "food_kg",
                "quantity": food_line["quantity"], "distance_km": food_line["distance_km"], "accessibility_score": food_line["accessibility_score"],
                "reasoning": food_line["reasoning"], "allocation_method": food_recommendation["method"],
            },
        ).json()
        client.post("/api/deliveries/dispatch", headers=auth_headers(warehouse_token), json={"allocation_id": food_approval["allocation_id"], "quantity_dispatched": food_line["quantity"]})
        short_delivery = round(food_line["quantity"] * 0.85, 1)  # intentional 15% shortfall
        mismatch = client.post("/api/deliveries/confirm", headers=auth_headers(relief_token), json={"allocation_id": food_approval["allocation_id"], "quantity_received": short_delivery}).json()
        print(f"  Dispatched {food_line['quantity']} food_kg, relief centre reports receiving only {short_delivery}.")
        print(f"  Result: {mismatch['status']} — discrepancy_id={mismatch.get('discrepancy_id')}, difference={mismatch.get('difference')}")

        _section("STEP 8 — AUDIT: blockchain transactions + audit log")
        chain_txs = client.get("/api/audit/blockchain/transactions").json()
        print(f"  {len(chain_txs)} on-chain transaction(s) recorded so far.")
        for tx in chain_txs[:6]:
            print(f"    {tx['event_type']} (entity #{tx['related_entity_id']}) -> {tx['tx_hash'][:18]}...")

        discrepancies = client.get("/api/deliveries/discrepancies").json()
        print(f"\n  Open discrepancies: {len([d for d in discrepancies if d['status'] == 'OPEN'])}")
        for d in discrepancies:
            print(f"    #{d['id']} allocation #{d['allocation_id']}: expected {d['expected_quantity']}, "
                  f"received {d['received_quantity']}, diff {d['difference']}, status={d['status']}")

        _section("DEMO SCENARIO COMPLETE")
        print("Open the Streamlit dashboard (`streamlit run dashboard/app.py`) or GET /api/audit")
        print("(as district_officer/auditor) to see this full trail rendered.")
        print("The discrepancy above was left OPEN intentionally — resolve it live via")
        print("POST /api/deliveries/discrepancies/resolve during the demo to show that flow too.")


if __name__ == "__main__":
    main()
