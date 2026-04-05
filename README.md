# Terra Alert

Terra Alert is a web-based AI-assisted disaster risk awareness system. It collects disaster-related
reports, classifies them, calculates risk percentages, and provides location-based alerts and
precautionary guidance.

## Quick Start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Initialize the database (optional, auto-created on first run):

```bash
python scripts/init_db.py
```

3. Run the app:

```bash
python run.py
```

Open `http://127.0.0.1:5000` in your browser.

## Risk Formula

Risk is computed per disaster type using a weighted score:

- **Base points** per report (`RISK_POINTS_PER_REPORT`, default `12`)
- **Severity weight** (`low=0.8`, `medium=1.0`, `high=1.3`)
- **Recency weight** via exponential decay with half-life (`RISK_HALF_LIFE_DAYS`, default `3`)

The per-type score is capped at `100` and mapped to risk levels:

- **Medium** at `>= 35`
- **High** at `>= 70`

Thresholds and weights are configurable via environment variables.

## Data Sources

Real RSS/official feeds are configured in `data/sources/data_sources.json` (USGS, GDACS, NOAA NHC, NOAA NWS alerts). The collector supports:

- RSS/Atom feeds (`feedparser`)
- USGS GeoJSON feeds
- NWS alerts JSON

## Alerts Persistence

Generated alerts are stored in SQLite (`alerts` table) with a simple dedupe window (`ALERT_DEDUPE_HOURS`). The `/alerts` page displays the persisted alerts.

## ML Pipeline

Run training using the labeled CSV in `ml/datasets/labeled/training_data.csv`:

```bash
python ml/train_model.py
```

This saves `ml/models/disaster_classifier.pkl` and `ml/models/metrics.json`. Classification falls back to keyword matching when the model is missing.

## Project Structure

- `app/` Flask app, services, and models
- `data/` data sources and guidance
- `ml/` model training/evaluation
- `scripts/` utility scripts
- `templates/` HTML templates
- `tests/` pytest tests
