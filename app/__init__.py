import os
from flask import Flask
from .db import init_db

def create_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_folder = os.path.join(base_dir, 'templates')
    static_folder = os.path.join(base_dir, 'static')

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder, instance_relative_config=False)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(base_dir, 'data', 'app.db'),
    )

    init_db(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
