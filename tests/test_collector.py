from app.services.data_collector import collect_disaster_data


def test_collect_from_mock_sources():
    sources = [
        {
            "name": "MockFeed",
            "mock_items": [
                {"title": "Cyclone warning", "content": "Storm surge expected"},
                {"title": "Earthquake tremor", "content": "Minor quake"},
            ],
        }
    ]

    items = collect_disaster_data(sources)
    assert len(items) == 2
    assert items[0]["source"] == "MockFeed"
