from app.utils import normalize_text


def filter_by_location(reports, location_text=None):
    if not location_text:
        return reports

    needle = normalize_text(location_text)
    if not needle:
        return reports

    filtered = []
    for report in reports:
        haystack = " ".join(
            [
                report.get("location", ""),
                report.get("title", ""),
                report.get("content", ""),
            ]
        )
        if needle in normalize_text(haystack):
            filtered.append(report)

    return filtered
