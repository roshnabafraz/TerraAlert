import json
from datetime import datetime, timezone

try:
    from dateutil import parser as date_parser
except ImportError:  # pragma: no cover
    date_parser = None


def load_json_file(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError:
        return default if default is not None else {}


def safe_parse_datetime(value):
    if not value:
        return None

    if isinstance(value, (int, float)):
        # Assume epoch milliseconds if value is large.
        if value > 10_000_000_000:
            return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
        return datetime.fromtimestamp(value, tz=timezone.utc)

    if isinstance(value, datetime):
        return value

    if date_parser:
        try:
            parsed = date_parser.parse(str(value))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except (ValueError, TypeError):
            pass

    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(str(value), fmt)
            return parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None
