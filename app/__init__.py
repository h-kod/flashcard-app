import os
from pathlib import Path
from flask import Flask, request
from .rate_limiter import init_limiter


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

    init_limiter(app)

    from .routes import bp
    app.register_blueprint(bp)

    # Error handler for rate limit exceeded
    @app.errorhandler(429)
    def rate_limit_handler(e):
        from flask import render_template, jsonify
        if request.is_json or request.content_type == 'application/json':
            return jsonify({
                'error': 'Çok fazla istek gönderdiniz. Lütfen biraz sonra tekrar deneyin.',
                'status': 429
            }), 429
        return render_template('error.html', 
                             title='429 - Çok Fazla İstek',
                             message='Çok fazla istek gönderdiniz. Lütfen biraz sonra tekrar deneyin.'), 429

    return app
