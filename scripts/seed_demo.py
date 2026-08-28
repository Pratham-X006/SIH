"""Seed SYNTHETIC PROTOTYPE OPERATIONAL DATA directly into the database: organizations,
login users, warehouses + inventory, and zones (from data/districts_sample.json).

This writes directly to the DB (not through the API) because there is deliberately no public
self-registration endpoint for creating DISTRICT_OFFICER/WAREHOUSE_MANAGER/etc. accounts —
that would be a real security hole in production. A seed script bootstrapping demo accounts
is the standard, honest way to get a reproducible demo state (Section 47).

Idempotent: re-running skips rows that already exist by unique name/username.

Usage (no backend process needs to be running for this step):
    python scripts/seed_demo.py

Then run scripts/run_demo_scenario.py against a running backend to exercise the actual
pipeline end-to-end via the real HTTP API.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.core.security import hash_password  # noqa: E402
from app.db.init_db import init_db  # noqa: E402
from app.db.models import Organization, ResourceInventory, User, Warehouse, Zone  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402

DISTRICTS_PATH = REPO_ROOT / "data" / "districts_sample.json"

ORGANIZATIONS = [
    {"name": "Nagaon District Administration", "org_type": "gov", "verified": True},
    {"name": "Assam SDRF Warehousing", "org_type": "warehouse", "verified": True},
    {"name": "Brahmaputra Relief Trust", "org_type": "ngo", "verified": True},
]

USERS = [
    {"username": "district_officer", "password": "demo-pass-1", "full_name": "Rina Sharma", "role": "DISTRICT_OFFICER", "org": "Nagaon District Administration"},
    {"username": "warehouse_mgr", "password": "demo-pass-2", "full_name": "Anil Bora", "role": "WAREHOUSE_MANAGER", "org": "Assam SDRF Warehousing"},
    {"username": "ngo_coordinator", "password": "demo-pass-3", "full_name": "Anand Deka", "role": "NGO", "org": "Brahmaputra Relief Trust"},
    {"username": "relief_centre", "password": "demo-pass-4", "full_name": "Nagaon Relief Centre", "role": "RELIEF_CENTRE", "org": "Brahmaputra Relief Trust"},
    {"username": "auditor", "password": "demo-pass-5", "full_name": "Priya Nair", "role": "AUDITOR", "org": "Nagaon District Administration"},
    {"username": "admin", "password": "demo-pass-0", "full_name": "System Administrator", "role": "SUPER_ADMIN", "org": "Nagaon District Administration"},
]

# Two warehouses on purpose: one closer-but-harder-to-reach, one farther-but-accessible —
# so the allocation engine's "don't just pick the nearest warehouse" behaviour (Section 19)
# has a real scenario to demonstrate.
WAREHOUSES = [
    {
        "name": "Kampur Forward Depot (near, flood-prone access road)",
        "org": "Assam SDRF Warehousing",
        "lat": 26.20, "lon": 92.42,
        "notes": "SYNTHETIC — closer to Nagaon town but its access road crosses a low-lying "
        "stretch that is itself flood-prone; modeled with a lower accessibility_score.",
        "inventory": {"food_kg": 8000, "water_litres": 40000, "medical_kits": 300, "shelter_units": 400},
    },
    {
        "name": "Guwahati Regional Warehouse (far, all-weather road)",
        "org": "Assam SDRF Warehousing",
        "lat": 26.14, "lon": 91.74,
        "notes": "SYNTHETIC — farther from Nagaon but on an all-weather highway, modeled "
        "with a higher accessibility_score.",
        "inventory": {"food_kg": 15000, "water_litres": 80000, "medical_kits": 500, "shelter_units": 600},
    },
    {
        "name": "Barpeta District Store",
        "org": "Assam SDRF Warehousing",
        "lat": 26.32, "lon": 91.01,
        "notes": "SYNTHETIC — secondary depot for the Barpeta/Kamrup comparison zones.",
        "inventory": {"food_kg": 6000, "water_litres": 30000, "medical_kits": 200, "shelter_units": 250},
    },
]


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        orgs_by_name: dict[str, Organization] = {o.name: o for o in db.query(Organization).all()}
        for spec in ORGANIZATIONS:
            if spec["name"] not in orgs_by_name:
                org = Organization(**spec)
                db.add(org)
                db.flush()
                orgs_by_name[org.name] = org
        db.commit()

        existing_usernames = {u.username for u in db.query(User).all()}
        for spec in USERS:
            if spec["username"] in existing_usernames:
                continue
            db.add(
                User(
                    username=spec["username"],
                    hashed_password=hash_password(spec["password"]),
                    full_name=spec["full_name"],
                    role=spec["role"],
                    org_id=orgs_by_name[spec["org"]].id,
                )
            )
        db.commit()

        existing_zone_names = {z.name for z in db.query(Zone).all()}
        districts = json.loads(DISTRICTS_PATH.read_text())["districts"]
        for d in districts:
            if d["name"] in existing_zone_names:
                continue
            db.add(
                Zone(
                    name=d["name"], state=d["state"], hazard_focus=d["hazard_focus"],
                    lat=d["centroid"]["lat"], lon=d["centroid"]["lon"],
                )
            )
        db.commit()

        existing_warehouse_names = {w.name for w in db.query(Warehouse).all()}
        for spec in WAREHOUSES:
            if spec["name"] in existing_warehouse_names:
                continue
            warehouse = Warehouse(
                name=spec["name"], org_id=orgs_by_name[spec["org"]].id,
                lat=spec["lat"], lon=spec["lon"], notes=spec["notes"],
            )
            db.add(warehouse)
            db.flush()
            for resource_type, qty in spec["inventory"].items():
                db.add(ResourceInventory(warehouse_id=warehouse.id, resource_type=resource_type, quantity_available=qty))
        db.commit()

        print("Seed complete (idempotent — safe to re-run).")
        print(f"  Organizations: {db.query(Organization).count()}")
        print(f"  Users:         {db.query(User).count()}  (see USERS list in this file for login credentials)")
        print(f"  Zones:         {db.query(Zone).count()}")
        print(f"  Warehouses:    {db.query(Warehouse).count()}")
        print()
        print("All warehouse/inventory/user data above is SYNTHETIC PROTOTYPE OPERATIONAL DATA.")
        print("Next: start the backend + blockchain node (see README.md), then run:")
        print("  python scripts/run_demo_scenario.py")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
