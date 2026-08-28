# Early-warning risk model — current state & upgrade path

**Current:** `scikit-learn` `LogisticRegression` over 5 engineered features from rolling
rainfall/soil-moisture windows (`rain_24h_mm`, `rain_72h_mm`, `rain_7d_mm`, `soil_moisture`,
`rain_intensity_max_mm_h`). Trained in `train.py` on **real historical daily rainfall pulled
live from Open-Meteo's Archive API** (`services.live_data.fetch_historical_rainfall`) for a
chosen lat/lon. There is no public ground-truth "flood occurred" label freely available for
arbitrary points at hackathon speed, so the training label is a **documented heuristic**:
a day is labeled high-risk if its 3-day rolling rainfall sum exceeds the 90th percentile of
the full historical window for that location. That's a real, defensible starting proxy — it's
approximately how many regional flood-warning thresholds are set — but it's a proxy, not
ground truth, and should be replaced with real historical flood/landslide incident records
(state disaster authority archives, NDMA post-disaster reports) as soon as the team has them.

**Upgrade path to what the PPT pitches (LSTM/CNN):**
1. Keep `train.py`'s feature-engineering + data-fetch as-is (it's genuinely reusable).
2. Swap `LogisticRegression` for a small `torch.nn.LSTM` or `keras` `Conv1D` stack taking the
   raw daily sequence as input rather than the 5 hand-engineered features.
3. Swap the heuristic label for real incident data once available.
4. Keep `predict(features) -> risk_score` as the interface the rest of the backend calls —
   nothing else needs to change when the model itself is upgraded.

Run training locally (needs internet access to Open-Meteo, so not from inside a
network-restricted sandbox):

```bash
python -m app.ml.train
```

This writes `app/ml/model.joblib`, loaded by `app/services/risk_model.py` at request time,
falling back to a fixed rainfall-threshold rule if no trained model file is present yet.
