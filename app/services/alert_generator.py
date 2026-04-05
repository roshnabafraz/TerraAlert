from datetime import datetime

from app.models import insert_alerts


def generate_alerts(risk_summary, location=None, persist=False, db_path=None, dedupe_hours=6):
    alerts = []
    overall = risk_summary.get("overall", {})
    level = overall.get("level", "low")
    top_type = overall.get("top_type") or "unknown"
    percentage = overall.get("percentage", 0)

    if level == "high":
        alerts.append(
            {
                "level": "high",
                "message": _format_message(
                    "High", top_type, location, "Stay alert and follow local guidance."
                ),
                "disaster_type": top_type,
                "location": location,
                "risk_percentage": percentage,
                "created_at": datetime.utcnow().isoformat(),
            }
        )
    elif level == "medium":
        alerts.append(
            {
                "level": "medium",
                "message": _format_message(
                    "Moderate", top_type, location, "Monitor updates and prepare."
                ),
                "disaster_type": top_type,
                "location": location,
                "risk_percentage": percentage,
                "created_at": datetime.utcnow().isoformat(),
            }
        )
    else:
        alerts.append(
            {
                "level": "low",
                "message": _format_message(
                    "Low", top_type, location, "No immediate action required."
                ),
                "disaster_type": top_type,
                "location": location,
                "risk_percentage": percentage,
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    if persist and db_path:
        insert_alerts(db_path, alerts, dedupe_hours=dedupe_hours)

    return alerts


def _format_message(prefix, disaster_type, location, suffix):
    location_text = f" in {location}" if location else ""
    return f"{prefix} risk of {disaster_type}{location_text}. {suffix}"
