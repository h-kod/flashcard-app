import sqlite3
from flask import g

from pathlib import Path

DATABASE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
'''


def get_db(app):
    if 'db' not in g:
        db_path = Path(app.config['DATABASE'])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(str(db_path))
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db(app)
        db.executescript(DATABASE_SCHEMA)
        db.commit()

    app.teardown_appcontext(close_db)
