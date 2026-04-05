from app.services.classifier import classify_reports


def test_keyword_classification():
    reports = [{"title": "Massive earthquake hits city", "content": "Seismic tremor"}]
    classified = classify_reports(reports)
    assert classified[0]["disaster_type"] == "earthquake"
    assert classified[0]["severity"] in {"high", "medium", "low"}
