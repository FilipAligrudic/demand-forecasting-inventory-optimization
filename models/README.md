# models/

This folder is created by `train_model.py`.

Generated files:
- `model_<Store>__<Product>.joblib` — trained LightGBM model bundle
- `forecast_<Store>__<Product>.csv` — forecast generated after training
- `metrics_<Store>__<Product>.csv` — model comparison metrics
- `training_summary.csv` — summary across all trained series
- `manifest.json` — training metadata

Model binaries are ignored by Git because they can be large.
