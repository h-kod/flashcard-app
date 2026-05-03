import os
from pathlib import Path
from flask import Flask
from .db import init_db


def load_env_file(base_dir: str) -> None:
    env_path = Path(base_dir) / '.env'
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def get_gemini_api_key() -> str:
    return os.environ.get('GEMINI_API_KEY', '').strip()


def create_app(test_config=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_folder = os.path.join(base_dir, 'templates')
    static_folder = os.path.join(base_dir, 'static')
    load_env_file(base_dir)

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
        instance_relative_config=False,
    )
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(base_dir, 'data', 'app.db'),
        GEMINI_API_KEY=get_gemini_api_key(),
        GEMINI_MODEL=os.environ.get('GEMINI_MODEL', 'models/gemma-3-1b-it'),
        GEMINI_API_ROOTS=[
            root.strip() for root in os.environ.get(
                'GEMINI_API_ROOTS',
                'https://generativelanguage.googleapis.com/v1',
            ).split(',')
            if root.strip()
        ],
    )

    if test_config:
        app.config.update(test_config)

    init_db(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
