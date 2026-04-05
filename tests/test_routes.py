from pathlib import Path

from app import create_app
from app.config import Config
from app.models.database import init_db


class TestConfig(Config):
    TESTING = True
    AUTO_INIT_DB = False
    DISABLE_REMOTE_FETCH = True


def test_routes_load(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    class LocalConfig(TestConfig):
        DB_PATH = db_path
        DATA_DIR = Path(__file__).resolve().parents[1] / "data"

    app = create_app(LocalConfig)
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200

    response = client.get("/dashboard")
    assert response.status_code == 200

    # new help page should render successfully; without any data file we expect
    # fallback Pakistan numbers to be present in the markup.
    response = client.get("/help")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Police" in html
    assert "1122" in html

    # test permanent location API
    # initially no location stored
    resp = client.get("/api/permanent-location?user_id=default_user")
    assert resp.status_code == 404

    # set a permanent location
    resp = client.post(
        "/api/permanent-location",
        json={"user_id": "default_user", "latitude": 24.8607, "longitude": 67.0011, "location_name": "Karachi"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("status") == "ok"

    # now GET should return stored data
    resp = client.get("/api/permanent-location?user_id=default_user")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("latitude") == 24.8607
    assert data.get("longitude") == 67.0011
    assert data.get("location_name") == "Karachi"

    # homepage should render permanent location information
    response = client.get("/")
    html = response.get_data(as_text=True)
    assert "Karachi" in html
    assert "id=\"home-map\"" in html
    assert "id=\"home-risk-notification\"" in html

    # remove the permanent location
    resp = client.delete(
        "/api/permanent-location",
        json={"user_id": "default_user"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("status") == "deleted"

    # verify it's gone
    resp = client.get("/api/permanent-location?user_id=default_user")
    assert resp.status_code == 404

    response = client.get("/")
    assert "Karachi" not in response.get_data(as_text=True)

