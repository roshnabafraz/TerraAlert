import json
from pathlib import Path
from typing import Optional, Dict, Any

from flask import current_app


_STORAGE_FILENAME = "permanent_locations.json"


def _get_storage_path() -> Path:
    data_dir = Path(current_app.config["DATA_DIR"])
    return data_dir / _STORAGE_FILENAME


def _read_storage() -> Dict[str, Any]:
    path = _get_storage_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_storage(data: Dict[str, Any]) -> None:
    path = _get_storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def get_permanent_location(user_id: str) -> Optional[Dict[str, Any]]:
    """Return the stored permanent location for a given user.

    The returned dictionary may contain keys ``latitude``, ``longitude`` and
    ``location_name``.  If no entry exists for the user an ``None`` value is
    returned.
    """
    data = _read_storage()
    return data.get(user_id)


def set_permanent_location(user_id: str, latitude: float, longitude: float, location_name: str) -> None:
    """Store or update a user's permanent location."""
    data = _read_storage()
    data[user_id] = {
        "latitude": latitude,
        "longitude": longitude,
        "location_name": location_name,
    }
    _write_storage(data)


def delete_permanent_location(user_id: str) -> None:
    """Remove a user's permanent location if it exists."""
    data = _read_storage()
    if user_id in data:
        del data[user_id]
        _write_storage(data)
