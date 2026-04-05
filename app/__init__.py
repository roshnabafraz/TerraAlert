from flask import Flask

from .config import Config
from .models.database import init_db
from . import routes


def create_app(config_class=Config):
    base_dir = getattr(config_class, "BASE_DIR", Config.BASE_DIR)
    template_dir = str(base_dir / "templates")
    static_dir = str(base_dir / "app" / "static")

    app = Flask(
        __name__,
        instance_relative_config=False,
        template_folder=template_dir,
        static_folder=static_dir,
    )
    app.config.from_object(config_class)

    if app.config.get("AUTO_INIT_DB"):
        init_db(app.config["DB_PATH"])

    routes.register_routes(app)
    return app
