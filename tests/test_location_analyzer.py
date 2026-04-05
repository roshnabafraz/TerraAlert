from app.services.location_analyzer import filter_by_location


def test_filter_by_location():
    reports = [
        {"title": "Flood in Lahore", "content": "Heavy rain", "location": "Lahore"},
        {"title": "Heatwave alert", "content": "Karachi", "location": "Karachi"},
    ]

    filtered = filter_by_location(reports, "Lahore")
    assert len(filtered) == 1
    assert filtered[0]["location"] == "Lahore"
