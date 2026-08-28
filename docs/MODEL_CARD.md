# Model Card — Flood Risk Baseline

## What this model predicts

A calibrated-looking probability (0-1) that a location is in a "high-risk" rainfall
regime, based on 4 engineered rolling-rainfall features. **This is not a flood occurrence
prediction** — it is a risk-score proxy, and the codebase and this document both say so
consistently (see `app/services/risk_model.py`, `app/ml/README.md`). The correct sentence to
say to a judge is: *"The model estimates a rainfall-based risk score for a location, trained
on real historical precipitation, using a documented proxy label because no free, ground-truth
flood-occurrence dataset was available at this project's timescale."* Not: "the AI predicts
floods."

## Algorithm and why

`scikit-learn` `LogisticRegression`, `class_weight="balanced"`. Chosen over LSTM/CNN because:

1. The training set is small (one location, up to ~2 years of daily rainfall) — not enough
   data to fit a deep sequence model without overfitting.
2. The feature set is 4 hand-engineered scalars (rolling rainfall sums + an intensity proxy),
   not a raw sequence — there is no long-range temporal structure here that an LSTM would
   exploit better than rolling-window features already capture.
3. Logistic regression is fully interpretable (coefficients map directly to feature
   contribution), which matters for the "why did the model say HIGH risk" explainability
   requirement.

The masterplan/frozen spec name XGBoost as the target primary model — not yet implemented in
this build; logistic regression is what's actually trained and serving today. The interface
(`predict(features) -> risk_score`) is designed so swapping the model class does not require
changing any caller (see `app/ml/README.md`'s stated upgrade path).

## Training data

Real historical daily rainfall from Open-Meteo's Archive API (`archive-api.open-meteo.com`)
for a chosen lat/lon, default window in `prepare_demo.py`: 365 days ending 2 days before the
run date, centered on Nagaon, Assam (26.35°N, 92.68°E).

## Label

`high_risk = 1` if a day's 3-day rolling rainfall sum is at or above the 90th percentile of
the pulled historical window for that location, else `0`. **This is a documented heuristic,
not a ground-truth flood/no-flood record.** No free, programmatically-accessible historical
flood-occurrence dataset for arbitrary Indian coordinates was integrated in this build (the
target architecture's Sentinel-1 SAR flood-extent labeling approach, described in the
masterplan for the Nagaon/Kopili basin specifically, requires Google Earth Engine access and
is not implemented here — see `LIMITATIONS.md`).

## Evaluation

`train.py` prints a `sklearn.metrics.classification_report` (precision/recall/F1 per class)
on a single held-out 20% split, stratified by label where possible. **This is a single
random split, not the event-level chronological split the frozen spec specifies** — with
under a year or two of daily data for one location, there usually aren't enough distinct
"events" to do a meaningful event-level split, so this metric should be read as a sanity
check that the classifier learned *something* from the features, not as a rigorous
generalization estimate. No PR-AUC, Brier score, or calibration curve is computed yet —
documented as a gap, not silently omitted.

## Known failure modes

- **False negative** (real elevated-risk conditions, model says low risk): the model has no
  mechanism to prevent this beyond `class_weight="balanced"`; no minimum-recall threshold
  tuning has been performed. This matters more than a false positive in a disaster-warning
  context and is flagged as unresolved, not silently accepted.
- **Untrained fallback**: if no `model.joblib` exists, `risk_model.py` returns
  `rain_72h_mm / 200` clamped to 1.0, explicitly labeled `"fallback_threshold_rule_untrained"`
  in every API response — callers and the UI can distinguish a real trained-model prediction
  from the fallback heuristic.
- **Single-location training**: a model trained on Nagaon's rainfall distribution has not
  been validated on any other location's distribution; using it elsewhere without retraining
  would be a coverage-shift risk.

## Versioning

`backend/app/db/models.py::ModelVersion` exists as a schema for tracking trained-model
metadata (algorithm, training data source, feature names, metrics, artifact path), but
`train.py` does not yet write a row there automatically — documented as a near-term gap.
