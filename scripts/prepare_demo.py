"""One-command demo readiness check + preparation (Section 77).

Does NOT start the backend/blockchain processes (those are long-running servers — see
run_demo.sh, or start them manually per README.md). What this script does:

  1. Verify data availability (districts_sample.json present and parseable)
  2. Seed synthetic operational data (organizations/users/warehouses/zones)
  3. Train the flood-risk model on REAL historical rainfall for Nagaon, Assam
  4. Report readiness of each component with a clear OK/WARN/FAIL per item

Usage:
    python scripts/prepare_demo.py
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

NAGAON_LAT, NAGAON_LON = 26.35, 92.68

results: list[tuple[str, str, str]] = []  # (component, status, detail)


def check(component: str, ok: bool, detail: str) -> None:
    results.append((component, "OK" if ok else "WARN", detail))


def main() -> None:
    districts_path = REPO_ROOT / "data" / "districts_sample.json"
    try:
        districts = json.loads(districts_path.read_text())["districts"]
        check("data availability", True, f"{len(districts)} districts in data/districts_sample.json")
    except Exception as exc:  # noqa: BLE001
        check("data availability", False, f"Could not read districts_sample.json: {exc}")
        _report_and_exit()
        return

    try:
        from scripts.seed_demo import seed  # type: ignore
    except ImportError:
        sys.path.insert(0, str(REPO_ROOT))
        from scripts.seed_demo import seed  # type: ignore
    try:
        seed()
        check("database seed", True, "organizations/users/warehouses/zones seeded (idempotent)")
    except Exception as exc:  # noqa: BLE001
        check("database seed", False, f"Seeding failed: {exc}")

    try:
        from app.ml.train import main as train_main

        asyncio.run(train_main(lat=NAGAON_LAT, lon=NAGAON_LON, days=365))
        check("ML model training", True, "Trained on REAL historical Open-Meteo rainfall for Nagaon (365 days)")
    except Exception as exc:  # noqa: BLE001
        check(
            "ML model training", False,
            f"Training failed ({exc}). The API will still work using the documented fallback "
            f"heuristic (see app/services/risk_model.py) but predictions will be labeled "
            f"'fallback_threshold_rule_untrained'.",
        )

    deployment_file = BACKEND_DIR / "app" / "services" / "relief_tracking_deployment.json"
    check(
        "blockchain deployment",
        deployment_file.exists(),
        "Contract deployment file found." if deployment_file.exists() else
        "Not deployed yet — run `npx hardhat node` then `npx hardhat run scripts/deploy.js "
        "--network localhost` in blockchain/ before the demo.",
    )

    _report_and_exit()


def _report_and_exit() -> None:
    print("\n" + "=" * 60)
    print("DEMO READINESS REPORT")
    print("=" * 60)
    any_fail = False
    for component, status, detail in results:
        marker = {"OK": "[OK]  ", "WARN": "[WARN]"}[status]
        print(f"{marker} {component}: {detail}")
        if status == "WARN":
            any_fail = True
    print("=" * 60)
    if any_fail:
        print("Some components need attention before a live demo — see WARN lines above.")
    else:
        print("All checks passed. Start the backend, then run scripts/run_demo_scenario.py.")
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
