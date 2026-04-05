from datetime import datetime, timezone

from app.utils import load_json_file, safe_parse_datetime

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

try:
    import feedparser
except ImportError:  # pragma: no cover
    feedparser = None


def load_sources(path):
    data = load_json_file(path, default={"sources": []})
    return data.get("sources", [])


def collect_disaster_data(sources, timeout=15, limit=200, user_agent=None):
    items = []
    for source in sources:
        if "mock_items" in source:
            items.extend(_normalize_items(source["mock_items"], source.get("name")))
            continue

        if not requests or not source.get("url"):
            continue

        source_type = source.get("type", "rss")
        headers = {"User-Agent": user_agent} if user_agent else {}

        try:
            response = requests.get(source["url"], headers=headers, timeout=timeout)
            response.raise_for_status()
        except Exception:
            continue

        if source_type in {"rss", "atom", "gdacs_rss", "nhc_rss"}:
            extracted = _extract_from_rss(response.text)
        elif source_type == "geojson_usgs":
            try:
                payload = response.json()
            except ValueError:
                continue
            extracted = _extract_from_usgs_geojson(payload)
        elif source_type == "nws_alerts":
            try:
                payload = response.json()
            except ValueError:
                continue
            extracted = _extract_from_nws_json(payload)
        else:
            extracted = []

        items.extend(_normalize_items(extracted, source.get("name"), source))

        if len(items) >= limit:
            break

    return _dedupe(items)[:limit]


def _extract_from_rss(text):
    if not feedparser:
        return []

    parsed = feedparser.parse(text)
    entries = []
    for entry in parsed.entries:
        published = None
        if hasattr(entry, "published"):
            published = entry.published
        elif hasattr(entry, "updated"):
            published = entry.updated

        entries.append(
            {
                "title": entry.get("title"),
                "content": entry.get("summary") or entry.get("description"),
                "source": entry.get("link"),
                "published_at": published,
                "location": entry.get("gdacs:country") or entry.get("geo:point"),
            }
        )
    return entries


def _extract_from_usgs_geojson(payload):
    features = payload.get("features", []) if isinstance(payload, dict) else []
    items = []
    for feature in features:
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coords = geometry.get("coordinates", [])
        place = props.get("place")
        magnitude = props.get("mag")
        time_ms = props.get("time")

        items.append(
            {
                "title": props.get("title") or "Earthquake event",
                "content": f"Magnitude {magnitude} earthquake at {place}" if place else props.get("title"),
                "source": props.get("url"),
                "published_at": safe_parse_datetime(time_ms),
                "location": place or _coords_to_text(coords),
                "disaster_type": "earthquake",
                "severity": _severity_from_magnitude(magnitude),
            }
        )
    return items


def _extract_from_nws_json(payload):
    features = payload.get("features", []) if isinstance(payload, dict) else []
    items = []
    for feature in features:
        props = feature.get("properties", {})
        items.append(
            {
                "title": props.get("headline") or props.get("event"),
                "content": props.get("description") or props.get("instruction"),
                "source": props.get("web"),
                "published_at": props.get("effective"),
                "location": props.get("areaDesc"),
                "disaster_type": _event_to_type(props.get("event")),
                "severity": (props.get("severity") or "").lower(),
            }
        )
    return items


def _normalize_items(items, source_name=None, source_config=None):
    normalized = []
    for item in items:
        published_at = item.get("published_at")
        parsed_dt = safe_parse_datetime(published_at)
        if parsed_dt:
            published_at = parsed_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            published_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        normalized.append(
            {
                "title": item.get("title", "Untitled"),
                "content": item.get("content", ""),
                "source": item.get("source", source_name),
                "published_at": published_at,
                "location": item.get("location"),
                "disaster_type": item.get("disaster_type")
                or (source_config or {}).get("default_type"),
                "severity": item.get("severity"),
            }
        )
    return normalized


def _dedupe(items):
    seen = set()
    unique = []
    for item in items:
        key = (item.get("title"), item.get("published_at"), item.get("source"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _coords_to_text(coords):
    if not coords or len(coords) < 2:
        return None
    return f"{coords[1]:.2f},{coords[0]:.2f}"


def _severity_from_magnitude(magnitude):
    if magnitude is None:
        return "low"
    try:
        mag = float(magnitude)
    except (TypeError, ValueError):
        return "low"
    if mag >= 6.5:
        return "high"
    if mag >= 5.0:
        return "medium"
    return "low"


def _event_to_type(event):
    if not event:
        return None
    event_lower = event.lower()
    if "heat" in event_lower:
        return "heatwave"
    if "flood" in event_lower:
        return "flood"
    if "hurricane" in event_lower or "tropical" in event_lower:
        return "cyclone"
    return None
