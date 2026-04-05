import json

from app.config import Config
from app.models.database import get_db_connection, init_db


if __name__ == "__main__":
    init_db(Config.DB_PATH)
    guidance_path = Config.DATA_DIR / "guidance" / "precautions.json"

    with open(guidance_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    tips_by_type = data.get("types", {})
    with get_db_connection(Config.DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM guidance")
        for disaster_type, tips in tips_by_type.items():
            cursor.execute(
                "INSERT INTO guidance (disaster_type, tips) VALUES (?, ?)",
                (disaster_type, json.dumps(tips)),
            )
        conn.commit()

    print("Guidance loaded into database")
