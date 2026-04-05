from pathlib import Path
import os


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "database" / "terra_alert.db"

    SECRET_KEY = os.environ.get("TERRA_ALERT_SECRET", "terra-alert-dev")
    JSON_SORT_KEYS = False

    RISK_WINDOW_DAYS = int(os.environ.get("RISK_WINDOW_DAYS", "7"))
    RISK_HALF_LIFE_DAYS = float(os.environ.get("RISK_HALF_LIFE_DAYS", "3"))
    RISK_POINTS_PER_REPORT = float(os.environ.get("RISK_POINTS_PER_REPORT", "12"))
    HIGH_RISK_THRESHOLD = int(os.environ.get("HIGH_RISK_THRESHOLD", "70"))
    MEDIUM_RISK_THRESHOLD = int(os.environ.get("MEDIUM_RISK_THRESHOLD", "35"))
    DIGD_MIN_REPORTS = int(os.environ.get("DIGD_MIN_REPORTS", "3"))

    SEVERITY_WEIGHTS = {
        "low": float(os.environ.get("SEVERITY_WEIGHT_LOW", "0.8")),
        "medium": float(os.environ.get("SEVERITY_WEIGHT_MEDIUM", "1.0")),
        "high": float(os.environ.get("SEVERITY_WEIGHT_HIGH", "1.3")),
    }

    ALERT_DEDUPE_HOURS = int(os.environ.get("ALERT_DEDUPE_HOURS", "6"))

    NWS_USER_AGENT = os.environ.get(
        "NWS_USER_AGENT",
        "TerraAlert/1.0 (contact: admin@example.com)",
    )

    DISABLE_REMOTE_FETCH = False
    AUTO_INIT_DB = True