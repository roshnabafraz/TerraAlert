from collections import Counter
from datetime import datetime, timedelta, timezone
import math

from app.utils import safe_parse_datetime


def calculate_risk_summary(
    reports,
    window_days=7,
    risk_points_per_report=12,
    medium_threshold=35,
    high_threshold=70,
    half_life_days=3,
    severity_weights=None,
):
    severity_weights = severity_weights or {"low": 0.8, "medium": 1.0, "high": 1.3}

    if not reports:
        return {
            "overall": {"percentage": 0, "level": "low", "top_type": None},
            "by_type": {},
            "total_reports": 0,
            "window_days": window_days,
        }

    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=window_days)
    recent_reports = []
    for report in reports:
        published = safe_parse_datetime(report.get("published_at"))
        if published and published >= cutoff:
            recent_reports.append(report)

    if not recent_reports:
        return {
            "overall": {"percentage": 0, "level": "low", "top_type": None},
            "by_type": {},
            "total_reports": 0,
            "window_days": window_days,
        }

    scores = Counter()
    now = datetime.now(tz=timezone.utc)

    for report in recent_reports:
        disaster_type = report.get("disaster_type") or "unknown"
        severity = (report.get("severity") or "low").lower()
        severity_weight = severity_weights.get(severity, 1.0)

        published = safe_parse_datetime(report.get("published_at")) or now
        age_days = max(0.0, (now - published).total_seconds() / 86400)
        recency_weight = math.exp(-age_days / max(half_life_days, 0.1))

        score = risk_points_per_report * severity_weight * recency_weight
        scores[disaster_type] += score

    by_type = {}
    for disaster_type, score in scores.items():
        percentage = min(100, round(score))
        by_type[disaster_type] = {
            "count": sum(1 for report in recent_reports if (report.get("disaster_type") or "unknown") == disaster_type),
            "percentage": percentage,
            "level": _risk_level(
                percentage, medium_threshold=medium_threshold, high_threshold=high_threshold
            ),
        }

    top_type, top_data = max(by_type.items(), key=lambda item: item[1]["percentage"])
    overall_percentage = top_data["percentage"]

    return {
        "overall": {
            "percentage": overall_percentage,
            "level": _risk_level(
                overall_percentage, medium_threshold=medium_threshold, high_threshold=high_threshold
            ),
            "top_type": top_type,
        },
        "by_type": by_type,
        "total_reports": len(recent_reports),
        "window_days": window_days,
    }


def _risk_level(percentage, medium_threshold=35, high_threshold=70):
    if percentage >= high_threshold:
        return "high"
    if percentage >= medium_threshold:
        return "medium"
    return "low"
