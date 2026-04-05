from datetime import datetime

from app.services.risk_calculator import calculate_risk_summary


def test_risk_summary_basic():
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    reports = [
        {"disaster_type": "flood", "published_at": now, "severity": "medium"},
        {"disaster_type": "flood", "published_at": now, "severity": "medium"},
        {"disaster_type": "flood", "published_at": now, "severity": "medium"},
    ]

    summary = calculate_risk_summary(
        reports,
        window_days=7,
        risk_points_per_report=12,
        medium_threshold=35,
        high_threshold=70,
        half_life_days=3,
        severity_weights={"low": 0.8, "medium": 1.0, "high": 1.3},
    )

    assert summary["overall"]["percentage"] == 36
    assert summary["overall"]["level"] == "medium"
    assert summary["overall"]["top_type"] == "flood"
