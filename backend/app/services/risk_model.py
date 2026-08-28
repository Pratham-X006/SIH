"""Loads the trained baseline risk model if present; otherwise falls back to a fixed,
clearly-labeled rainfall-threshold rule so the API still returns something sane before
training has been run. See app/ml/README.md for upgrade path to LSTM/CNN."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import joblib
import numpy as np

MODEL_PATH = Path(__file__).parent.parent / "ml" / "model.joblib"

RiskLevel = Literal["low", "moderate", "high", "severe"]


def _bucket(score: float) -> RiskLevel:
    if score >= 0.75:
        return "severe"
    if score >= 0.5:
        return "high"
    if score >= 0.25:
        return "moderate"
    return "low"


class RiskModel:
    def __init__(self) -> None:
        self._model = None
        self._feature_names: list[str] = []
        self._is_trained = False
        if MODEL_PATH.exists():
            bundle = joblib.load(MODEL_PATH)
            self._model = bundle["model"]
            self._feature_names = bundle["feature_names"]
            self._is_trained = True

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def predict(
        self,
        rain_24h_mm: float,
        rain_72h_mm: float,
        rain_7d_mm: float,
        rain_intensity_max_mm_h: float,
    ) -> dict:
        features = {
            "rain_24h_mm": rain_24h_mm,
            "rain_72h_mm": rain_72h_mm,
            "rain_7d_mm": rain_7d_mm,
            "rain_intensity_max_mm_h": rain_intensity_max_mm_h,
        }

        if self._is_trained:
            x = np.array([[features[name] for name in self._feature_names]])
            score = float(self._model.predict_proba(x)[0, 1])
            source = "trained_logistic_regression"
        else:
            # Fallback heuristic — explicit and simple, used only until train.py has been run.
            score = min(1.0, rain_72h_mm / 200.0)
            source = "fallback_threshold_rule_untrained"

        return {
            "risk_score": round(score, 4),
            "risk_level": _bucket(score),
            "model_source": source,
            "features_used": features,
        }


# Module-level singleton so FastAPI routes share one loaded model.
risk_model = RiskModel()
