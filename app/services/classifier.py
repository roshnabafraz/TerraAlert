from pathlib import Path

from app.utils import normalize_text

try:
    import joblib
except ImportError:  # pragma: no cover
    joblib = None


KEYWORDS = {
    "flood": ["flood", "flooding", "flash flood", "overflow"],
    "earthquake": ["earthquake", "seismic", "tremor", "aftershock"],
    "heatwave": ["heatwave", "heat wave", "extreme heat", "record heat", "heat advisory"],
    "cyclone": ["cyclone", "hurricane", "typhoon", "storm surge", "tropical storm"],
}

MODEL_PATH = Path(__file__).resolve().parents[2] / "ml" / "models" / "disaster_classifier.pkl"


def classify_reports(reports):
    model = _load_model()
    classified = []

    for report in reports:
        report = report.copy()
        existing_type = (report.get("disaster_type") or "").lower()
        text = f"{report.get('title', '')} {report.get('content', '')}".strip()

        if existing_type and existing_type != "unknown":
            disaster_type = existing_type
        elif model:
            disaster_type = _predict_with_model(model, text)
        else:
            disaster_type = _keyword_classify(text)

        report["disaster_type"] = disaster_type
        report["severity"] = report.get("severity") or _estimate_severity(text)
        classified.append(report)

    return classified


def _load_model():
    if not joblib:
        return None
    if not MODEL_PATH.exists() or MODEL_PATH.stat().st_size < 10:
        return None

    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def _predict_with_model(model, text):
    try:
        prediction = model.predict([text])
        if prediction:
            return str(prediction[0])
    except Exception:
        return _keyword_classify(text)
    return _keyword_classify(text)


def _keyword_classify(text):
    normalized = normalize_text(text)
    for disaster_type, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                return disaster_type
    return "unknown"


def _estimate_severity(text):
    normalized = normalize_text(text)
    if any(word in normalized for word in ["catastrophic", "deadly", "massive", "major"]):
        return "high"
    if any(word in normalized for word in ["severe", "warning", "evacuation", "alert"]):
        return "medium"
    return "low"
