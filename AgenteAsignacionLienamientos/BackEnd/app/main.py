from pathlib import Path
import sys

from flask import Flask
from flask_cors import CORS


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.routes import router
from app.core.config import get_settings


settings = get_settings()
ALWAYS_ALLOWED_ORIGINS = [
    "https://agente-asignacion-lineamientos.vercel.app",
]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["APP_NAME"] = settings.app_name
    allowed_origins = list(dict.fromkeys([*settings.cors_origins, *ALWAYS_ALLOWED_ORIGINS]))
    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    app.register_blueprint(router)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=settings.app_host, port=settings.app_port, debug=settings.app_env == "dev")
