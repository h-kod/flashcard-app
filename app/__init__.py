import os
from flask import Flask
from .db import init_db


def get_gemini_api_key(base_dir: str) -> str:
    env_key = os.environ.get('GEMINI_API_KEY')
    if env_key:
        return env_key.strip()

    key_file = os.path.join(base_dir, 'gemini_key.txt')
    try:
        with open(key_file, encoding='utf-8') as handle:
            return handle.read().strip()
    except FileNotFoundError:
        return ''


def create_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_folder = os.path.join(base_dir, 'templates')
    static_folder = os.path.join(base_dir, 'static')

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
        instance_relative_config=False,
    )
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(base_dir, 'data', 'app.db'),
        GEMINI_API_KEY=get_gemini_api_key(base_dir),
        GEMINI_MODEL=os.environ.get('GEMINI_MODEL', 'models/gemma-3-1b-it'),
        GEMINI_API_ROOTS=[
            root.strip() for root in os.environ.get(
                'GEMINI_API_ROOTS',
                'https://generativelanguage.googleapis.com/v1',
            ).split(',')
            if root.strip()
        ],
    )

    init_db(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
