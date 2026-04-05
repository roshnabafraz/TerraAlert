from collections import defaultdict

from app.utils import normalize_text


HIGH_SIGNAL_KEYWORDS = ["evacuation", "warning", "disaster", "catastrophic", "deadly"]


def detect_information_gaps(reports, min_reports=3):
    if not reports:
        return []

    grouped = defaultdict(list)
    for report in reports:
        location = report.get("location") or "Unknown"
        grouped[location].append(report)

    gaps = []
    for location, items in grouped.items():
        count = len(items)
        high_signal = _has_high_signal(items)
        if high_signal and count < min_reports:
            gaps.append({"location": location, "count": count, "reason": "high_signal_low_coverage"})

    return gaps


def _has_high_signal(items):
    for report in items:
        severity = (report.get("severity") or "").lower()
        if severity == "high":
            return True

        text = " ".join([report.get("title", ""), report.get("content", "")])
        normalized = normalize_text(text)
        if any(keyword in normalized for keyword in HIGH_SIGNAL_KEYWORDS):
            return True

    return False
