from app.config import Config
from app.models.database import init_db


if __name__ == "__main__":
    init_db(Config.DB_PATH)
    print(f"Initialized database at {Config.DB_PATH}")
