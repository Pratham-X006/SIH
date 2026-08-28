"""
Train the baseline flood-risk classifier on REAL historical rainfall pulled live from
Open-Meteo's Archive API. See README.md in this folder for exactly what's real vs. a
documented proxy here.

Usage (needs outbound internet — run locally, not inside a network-restricted sandbox):
    python -m app.ml.train --lat 11.685 --lon 76.132 --days 730
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from app.services.live_data import fetch_historical_rainfall

MODEL_PATH = Path(__file__).parent / "model.joblib"
FEATURE_NAMES = ["rain_24h_mm", "rain_72h_mm", "rain_7d_mm", "rain_intensity_max_mm_h"]


def build_features(daily: dict) -> pd.DataFrame:
    """Turn Open-Meteo's daily archive payload into rolling-window features per day."""
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(daily["time"]),
            "rain_mm": daily["precipitation_sum"],
            "rain_hours": daily["precipitation_hours"],
        }
    ).sort_values("date").reset_index(drop=True)

    df["rain_24h_mm"] = df["rain_mm"]
    df["rain_72h_mm"] = df["rain_mm"].rolling(3, min_periods=1).sum()
    df["rain_7d_mm"] = df["rain_mm"].rolling(7, min_periods=1).sum()
    # crude intensity proxy: mm per hour of rain that day (avoids div-by-zero on dry days)
    df["rain_intensity_max_mm_h"] = df["rain_mm"] / df["rain_hours"].replace(0, np.nan)
    df["rain_intensity_max_mm_h"] = df["rain_intensity_max_mm_h"].fillna(0)

    # Documented heuristic label — see ml/README.md — NOT ground-truth flood/landslide data.
    threshold = df["rain_72h_mm"].quantile(0.90)
    df["high_risk"] = (df["rain_72h_mm"] >= threshold).astype(int)
    return df.dropna(subset=FEATURE_NAMES)


async def main(lat: float, lon: float, days: int) -> None:
    print(f"Fetching {days} days of real historical rainfall for ({lat}, {lon})...")
    payload = await fetch_historical_rainfall(lat, lon, days_back=days)
    daily = payload["daily"]
    df = build_features(daily)
    print(f"Built {len(df)} labeled daily samples "
          f"({df['high_risk'].sum()} high-risk / {len(df)} total).")

    X = df[FEATURE_NAMES].values
    y = df["high_risk"].values
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if y.sum() > 1 else None
    )

    clf = LogisticRegression(class_weight="balanced", max_iter=1000)
    clf.fit(X_train, y_train)

    print(classification_report(y_test, clf.predict(X_test), zero_division=0))

    joblib.dump({"model": clf, "feature_names": FEATURE_NAMES}, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lat", type=float, default=11.685, help="Wayanad, Kerala by default")
    parser.add_argument("--lon", type=float, default=76.132)
    parser.add_argument("--days", type=int, default=730)
    args = parser.parse_args()
    asyncio.run(main(args.lat, args.lon, args.days))
