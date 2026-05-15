from pathlib import Path
import sys

from flask import Flask
from flask_cors import CORS


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.routes import router
from app.core.config import get_settings


settings = get_settings()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["APP_NAME"] = settings.app_name
    CORS(app, origins=settings.cors_origins)
    app.register_blueprint(router)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=settings.app_host, port=settings.app_port, debug=settings.app_env == "dev")
