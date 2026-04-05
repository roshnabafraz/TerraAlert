from app.config import Config
from app.models.database import insert_reports
from app.services import (
    collect_disaster_data,
    classify_reports,
    load_sources,
    calculate_risk_summary,
    generate_alerts,
)


def run_once():
    sources = load_sources(Config.DATA_DIR / "sources" / "data_sources.json")
    collected = collect_disaster_data(sources, user_agent=Config.NWS_USER_AGENT)
    classified = classify_reports(collected)
    insert_reports(Config.DB_PATH, classified)

    risk_summary = calculate_risk_summary(
        classified,
        window_days=Config.RISK_WINDOW_DAYS,
        risk_points_per_report=Config.RISK_POINTS_PER_REPORT,
        medium_threshold=Config.MEDIUM_RISK_THRESHOLD,
        high_threshold=Config.HIGH_RISK_THRESHOLD,
        half_life_days=Config.RISK_HALF_LIFE_DAYS,
        severity_weights=Config.SEVERITY_WEIGHTS,
    )

    alerts = generate_alerts(
        risk_summary,
        location=None,
        persist=True,
        db_path=Config.DB_PATH,
        dedupe_hours=Config.ALERT_DEDUPE_HOURS,
    )

    return len(classified), len(alerts)


if __name__ == "__main__":
    report_count, alert_count = run_once()
    print(f"Stored {report_count} reports and {alert_count} alerts")
